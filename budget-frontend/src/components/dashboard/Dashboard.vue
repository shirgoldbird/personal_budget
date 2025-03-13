<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Personal Budget Dashboard</h1>
      <div class="mt-4 md:mt-0">
        <TellerConnect v-if="!bankStore.hasInstitutions" />
        <button v-else @click="exportToSheets" class="btn btn-outline ml-2">
          Export to Google Sheets
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="bankStore.loading || transactionStore.loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading...</p>
    </div>

    <!-- Error message -->
    <div v-else-if="bankStore.error || transactionStore.error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">
            {{ bankStore.error || transactionStore.error }}
          </p>
        </div>
      </div>
    </div>

    <!-- No connected banks yet -->
    <div v-else-if="!bankStore.hasInstitutions" class="bg-white shadow rounded-lg p-6 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
      </svg>
      <h3 class="mt-2 text-lg font-medium text-gray-900">No bank accounts connected</h3>
      <p class="mt-1 text-gray-500">Connect your bank accounts to start tracking your spending</p>
      <div class="mt-6">
        <TellerConnect />
      </div>
    </div>

    <!-- Dashboard content when banks are connected -->
    <div v-else>
      <!-- Month selector -->
      <div class="flex justify-between items-center mb-6">
        <button @click="transactionStore.setPreviousMonth" class="btn btn-outline">
          <span class="sr-only">Previous month</span>
          &larr;
        </button>
        <h2 class="text-xl font-semibold text-gray-900">
          {{ new Date(transactionStore.currentYear, transactionStore.currentMonth).toLocaleDateString(undefined, { month: 'long', year: 'numeric' }) }}
        </h2>
        <button @click="transactionStore.setNextMonth" class="btn btn-outline">
          <span class="sr-only">Next month</span>
          &rarr;
        </button>
      </div>

      <!-- Spending summary cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="card bg-primary-50">
          <h3 class="text-lg font-medium text-gray-900 mb-2">Income</h3>
          <p class="text-2xl font-bold text-primary-700">
            ${{ transactionStore.totalIncome.toFixed(2) }}
          </p>
        </div>
        
        <div class="card bg-red-50">
          <h3 class="text-lg font-medium text-gray-900 mb-2">Expenses</h3>
          <p class="text-2xl font-bold text-red-600">
            ${{ transactionStore.totalExpenses.toFixed(2) }}
          </p>
        </div>
        
        <div class="card bg-green-50">
          <h3 class="text-lg font-medium text-gray-900 mb-2">Balance</h3>
          <p class="text-2xl font-bold" :class="{ 'text-green-600': netBalance >= 0, 'text-red-600': netBalance < 0 }">
            ${{ netBalance.toFixed(2) }}
          </p>
        </div>
      </div>

      <!-- Spending by category chart -->
      <div class="card mb-8">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Spending by Category</h3>
        <div v-if="transactionStore.spendingByCategory.length === 0" class="text-center py-8 text-gray-500">
          No spending data for this month
        </div>
        <SpendingChart v-else :spending-data="transactionStore.spendingByCategory" />
      </div>

      <!-- Connected banks -->
      <div class="card mb-8">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">Connected Banks</h3>
          <router-link to="/accounts" class="text-primary-600 hover:text-primary-800 text-sm font-medium">
            View All Accounts
          </router-link>
        </div>
        
        <div class="space-y-4">
          <div v-for="institution in bankStore.institutions" :key="institution.institution_name" 
               class="border-b border-gray-200 pb-4 last:border-0 last:pb-0">
            <div class="flex justify-between items-center mb-2">
              <h4 class="font-medium text-gray-900">{{ institution.institution_name }}</h4>
              <div class="flex space-x-2">
                <button @click="viewAccounts(institution.institution_name)" class="btn btn-primary text-sm">
                  View Accounts
                </button>
                <button @click="disconnectBank(institution.institution_name)" class="btn btn-danger text-sm">
                  Disconnect
                </button>
              </div>
            </div>
            
            <!-- Show account summary -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 mt-2">
              <div v-for="account in getTopAccountsForInstitution(institution.institution_name, 3)" 
                   :key="account.id"
                   class="text-sm bg-gray-50 p-2 rounded">
                <div class="font-medium">{{ account.name }}</div>
                <div class="text-gray-500">Ending in {{ account.last_four }}</div>
              </div>
              <div v-if="getAccountsForInstitution(institution.institution_name).length > 3"
                   class="text-sm text-primary-600 flex items-center justify-center">
                +{{ getAccountsForInstitution(institution.institution_name).length - 3 }} more accounts
              </div>
            </div>
          </div>
        </div>
        
        <div class="mt-4 pt-4 border-t border-gray-200">
          <TellerConnect />
        </div>
      </div>

      <!-- Recent transactions -->
      <div class="card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">Recent Transactions</h3>
          <router-link to="/transactions" class="text-primary-600 hover:text-primary-800 text-sm font-medium">
            View All
          </router-link>
        </div>
        
        <div v-if="transactionStore.currentMonthTransactions.length === 0" class="text-center py-8 text-gray-500">
          No transactions for this month
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="transaction in recentTransactions" :key="transaction.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ new Date(transaction.date).toLocaleDateString() }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ transaction.description }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span v-if="transaction.category" class="px-2 py-1 rounded-full text-xs" 
                        :style="{ backgroundColor: getCategoryColor(transaction.category), color: 'white' }">
                    {{ transaction.category }}
                  </span>
                  <span v-else class="px-2 py-1 bg-gray-100 rounded-full text-xs text-gray-800">
                    Uncategorized
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-right"
                    :class="{ 'text-green-600': Number(transaction.amount) > 0, 'text-red-600': Number(transaction.amount) < 0 }">
                  ${{ Math.abs(parseFloat(transaction.amount)).toFixed(2) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useBankStore } from '../../stores/bankStore';
import { useTransactionStore } from '../../stores/transactionStore';
import TellerConnect from '../accounts/TellerConnect.vue';
import SpendingChart from './SpendingChart.vue';
import { apiService } from '../../services/api';

const router = useRouter();
const bankStore = useBankStore();
const transactionStore = useTransactionStore();

// Limit to showing only the 5 most recent transactions
const recentTransactions = computed(() => {
  return [...transactionStore.currentMonthTransactions]
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5);
});

const netBalance = computed(() => {
  return transactionStore.totalIncome - transactionStore.totalExpenses;
});

// Get color for a category
function getCategoryColor(categoryName) {
  const category = transactionStore.categories.find(c => c.name === categoryName);
  return category?.color || '#9CA3AF'; // Default gray color
}

// Function to view accounts for a specific institution
function viewAccounts(institutionName) {
  bankStore.selectedInstitution = institutionName;
  router.push('/accounts');
}

// Helper function to get accounts by institution
function getAccountsForInstitution(institutionName) {
  if (!bankStore._allAccounts) return [];
  return bankStore._allAccounts.filter(
    account => account.institution?.name === institutionName
  );
}

// Helper function to get a limited number of accounts for an institution
function getTopAccountsForInstitution(institutionName, limit) {
  const accounts = getAccountsForInstitution(institutionName);
  return accounts.slice(0, limit);
}

// Function to disconnect a bank
async function disconnectBank(institutionName) {
  if (confirm(`Are you sure you want to disconnect ${institutionName}?`)) {
    await bankStore.disconnectInstitution(institutionName);
  }
}

// Function to export transactions to Google Sheets
async function exportToSheets() {
  try {
    await transactionStore.exportTransactions();
    alert('Transactions exported to Google Sheets successfully!');
  } catch (error) {
    console.error('Export failed:', error);
  }
}

onMounted(async () => {
  // Fetch institutions, categories, and category mappings
  await bankStore.fetchInstitutions();
  await transactionStore.fetchCategories();
  await transactionStore.fetchCategoryMappings();
  
  // Fetch all transactions if institutions are available
  if (bankStore.hasInstitutions) {
    // Show loading state
    transactionStore.setLoading(true);
    
    try {
      // Fetch all accounts first
      const accountsPromises = bankStore.institutions.map(institution => 
        apiService.listAccounts(institution.institution_name)
          .then(accounts => {
            // Store all accounts in the bankStore
            accounts.forEach(account => {
              account.institution = {
                name: institution.institution_name,
                id: institution.institution_id
              };
            });
            
            if (!bankStore._allAccounts) bankStore._allAccounts = [];
            bankStore._allAccounts = [...bankStore._allAccounts, ...accounts];
            
            return accounts;
          })
      );
      
      const allAccountsArrays = await Promise.all(accountsPromises);
      const allAccounts = allAccountsArrays.flat();
      
      // Fetch transactions for all accounts in parallel
      const transactionPromises = allAccounts.map(account => {
        const institutionName = account.institution?.name;
        if (institutionName) {
          return apiService.listTransactions(account.id, institutionName)
            .then(transactions => {
              transactionStore.addTransactions(transactions);
              return transactions;
            })
            .catch(err => {
              console.error(`Error fetching transactions for account ${account.id}:`, err);
              return [];
            });
        }
        return Promise.resolve([]);
      });
      
      await Promise.all(transactionPromises);
    } catch (error) {
      console.error("Error fetching accounts or transactions:", error);
      transactionStore.setError("Failed to load some data. Please try refreshing.");
    } finally {
      transactionStore.setLoading(false);
    }
  }
});
</script>