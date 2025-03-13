import { defineStore } from "pinia";
import { apiService } from "../services/api";
import { useBankStore } from "./bankStore";

export const useTransactionStore = defineStore("transaction", {
  state: () => ({
    transactions: [],
    filteredTransactions: [],
    categories: [],
    categoryMappings: {},
    currentMonth: new Date().getMonth(),
    currentYear: new Date().getFullYear(),
    loading: false,
    error: null,
  }),

  getters: {
    hasTransactions: (state) => state.transactions.length > 0,

    // Get transactions for the current month/year
    currentMonthTransactions: (state) => {
      const startDate = new Date(state.currentYear, state.currentMonth, 1);
      const endDate = new Date(state.currentYear, state.currentMonth + 1, 0);

      return state.transactions.filter((tx) => {
        const txDate = new Date(tx.date);
        return txDate >= startDate && txDate <= endDate;
      });
    },

    // Get spending by category for current month
    spendingByCategory: (state) => {
      const transactions = state.currentMonthTransactions;
      const spendingMap = {};

      transactions.forEach((tx) => {
        // Only count expenses (negative amounts)
        if (parseFloat(tx.amount) < 0) {
          const category = tx.category || "Uncategorized";
          const amount = Math.abs(parseFloat(tx.amount));

          if (spendingMap[category]) {
            spendingMap[category] += amount;
          } else {
            spendingMap[category] = amount;
          }
        }
      });

      // Convert to array for easier rendering in charts
      return Object.entries(spendingMap).map(([category, amount]) => ({
        category,
        amount,
        // Find the color for this category
        color:
          state.categories.find((c) => c.name === category)?.color || "#9CA3AF",
      }));
    },

    // Get total income for current month
    totalIncome: (state) => {
      return state.currentMonthTransactions
        .filter((tx) => parseFloat(tx.amount) > 0)
        .reduce((sum, tx) => sum + parseFloat(tx.amount), 0);
    },

    // Get total expenses for current month
    totalExpenses: (state) => {
      return state.currentMonthTransactions
        .filter((tx) => parseFloat(tx.amount) < 0)
        .reduce((sum, tx) => sum + Math.abs(parseFloat(tx.amount)), 0);
    },

    // Get uncategorized transactions
    uncategorizedTransactions: (state) => {
      return state.transactions.filter(
        (tx) => !tx.category || tx.category === "Uncategorized"
      );
    },

    // For month selection in the UI
    availableMonths: (state) => {
      const months = new Set();

      state.transactions.forEach((tx) => {
        const date = new Date(tx.date);
        const monthYear = `${date.getFullYear()}-${date.getMonth()}`;
        months.add(monthYear);
      });

      return Array.from(months)
        .map((monthYear) => {
          const [year, month] = monthYear.split("-");
          return {
            year: parseInt(year),
            month: parseInt(month),
            label: new Date(parseInt(year), parseInt(month)).toLocaleDateString(
              undefined,
              { month: "long", year: "numeric" }
            ),
          };
        })
        .sort((a, b) => {
          if (a.year !== b.year) return b.year - a.year;
          return b.month - a.month;
        });
    },
  },

  actions: {
    async fetchTransactions(accountId, institution) {
      this.loading = true;
      this.error = null;

      try {
        const transactions = await apiService.listTransactions(
          accountId,
          institution
        );
        // If we're fetching for a specific account, we'll replace existing transactions
        // for that account and keep transactions from other accounts
        if (accountId) {
          // Remove existing transactions for this account
          this.transactions = this.transactions.filter(
            (tx) => tx.account_id !== accountId
          );
          // Add the new transactions
          this.transactions = [...this.transactions, ...transactions];
        } else {
          // If no account specified, just add the transactions (used when loading all)
          this.transactions = [...this.transactions, ...transactions];
        }
        this.filteredTransactions = [...this.transactions];
      } catch (err) {
        this.error = err.message || "Failed to fetch transactions";
        console.error(this.error);
      } finally {
        this.loading = false;
      }
    },

    // Set loading state directly
    setLoading(state) {
      this.loading = state;
    },

    // Set error state directly
    setError(message) {
      this.error = message;
    },

    // Add transactions to the store (used when loading transactions from multiple accounts)
    addTransactions(transactions) {
      if (!transactions || !transactions.length) return;

      // Get the account ID from the first transaction
      const accountId = transactions[0].account_id;

      // Remove existing transactions for this account
      this.transactions = this.transactions.filter(
        (tx) => tx.account_id !== accountId
      );

      // Add the new transactions
      this.transactions = [...this.transactions, ...transactions];
      this.filteredTransactions = [...this.transactions];
    },

    async fetchCategories() {
      this.loading = true;

      try {
        this.categories = await apiService.getCategories();
      } catch (err) {
        this.error = err.message || "Failed to fetch categories";
        console.error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async fetchCategoryMappings() {
      this.loading = true;

      try {
        this.categoryMappings = await apiService.getMappings();
      } catch (err) {
        this.error = err.message || "Failed to fetch category mappings";
        console.error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async categorizeTransaction(transactionId, categoryName) {
      const transaction = this.transactions.find(
        (tx) => tx.id === transactionId
      );
      if (!transaction) return;

      // Update locally first for immediate UI feedback
      transaction.category = categoryName;

      // Get account name for the transaction
      const account = this.getAccountById(transaction.account_id);
      const accountName = account
        ? `${account.institution?.name || "Unknown"} - ${account.name} (${
            account.last_four
          })`
        : "Unknown Account";

      // Then send to API with both account_id and account_name
      try {
        const txWithAccountName = {
          ...transaction,
          account_name: accountName,
        };

        await apiService.categorizeTransactions([txWithAccountName]);
      } catch (err) {
        this.error = err.message || "Failed to categorize transaction";
        console.error(this.error);
        // Revert local change if API call fails
        transaction.category = null;
      }
    },

    async exportTransactions() {
      this.loading = true;

      try {
        // Format transactions for export
        const formattedTransactions = this.currentMonthTransactions.map(
          (tx) => {
            // Get account information from bank store
            const account = this.getAccountById(tx.account_id);
            const accountName = account
              ? `${account.institution?.name || "Unknown"} - ${account.name} (${
                  account.last_four
                })`
              : "Unknown Account";

            return {
              id: tx.id,
              date: tx.date,
              account_id: tx.account_id, // Keep the required account_id field
              account_name: accountName, // Add account name as additional field
              description: tx.description,
              amount: tx.amount,
              category: tx.category || "Uncategorized",
              notes: tx.notes || "",
            };
          }
        );

        // The API expects an object with a transactions property that is an array
        await apiService.exportTransactions({
          transactions: formattedTransactions,
        });

        return true;
      } catch (err) {
        this.error = err.message || "Failed to export transactions";
        console.error(this.error);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // Helper to get account information from bank store
    getAccountById(accountId) {
      const bankStore = useBankStore();
      if (bankStore._allAccounts) {
        return bankStore._allAccounts.find((acc) => acc.id === accountId);
      }
      return null;
    },

    setMonth(month, year) {
      this.currentMonth = month;
      this.currentYear = year;
    },

    setNextMonth() {
      if (this.currentMonth === 11) {
        this.currentMonth = 0;
        this.currentYear++;
      } else {
        this.currentMonth++;
      }
    },

    setPreviousMonth() {
      if (this.currentMonth === 0) {
        this.currentMonth = 11;
        this.currentYear--;
      } else {
        this.currentMonth--;
      }
    },

    filterTransactions(searchText) {
      if (!searchText) {
        this.filteredTransactions = [...this.transactions];
        return;
      }

      const query = searchText.toLowerCase();
      this.filteredTransactions = this.transactions.filter(
        (tx) =>
          tx.description.toLowerCase().includes(query) ||
          (tx.category && tx.category.toLowerCase().includes(query))
      );
    },

    reset() {
      this.transactions = [];
      this.filteredTransactions = [];
      this.error = null;
    },
  },
});
