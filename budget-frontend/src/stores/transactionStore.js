import { defineStore } from "pinia";
import { apiService } from "../services/api";

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
        this.transactions = transactions;
        this.filteredTransactions = [...transactions];
      } catch (err) {
        this.error = err.message || "Failed to fetch transactions";
        console.error(this.error);
      } finally {
        this.loading = false;
      }
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

      // Then send to API
      try {
        await apiService.categorizeTransactions([transaction]);
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
        await apiService.exportTransactions({
          transactions: this.currentMonthTransactions,
        });
      } catch (err) {
        this.error = err.message || "Failed to export transactions";
        console.error(this.error);
      } finally {
        this.loading = false;
      }
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
