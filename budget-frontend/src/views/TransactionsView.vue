<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Transactions</h1>
        <p class="text-gray-600">
          {{ bankStore.selectedAccount ? `Filtering by: ${bankStore.selectedAccount.name}` : 'All accounts' }}
        </p>
      </div>
      <div class="mt-4 md:mt-0 flex space-x-2">
        <button @click="clearAccountFilter" v-if="bankStore.selectedAccount" class="btn btn-outline">
          Show All Accounts
        </button>
        <button @click="exportTransactions" class="btn btn-primary">
          Export to Google Sheets
        </button>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="transactionStore.loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading transactions...</p>
    </div>

    <!-- Error message -->
    <div v-else-if="transactionStore.error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">
            {{ transactionStore.error }}
          </p>
        </div>
      </div>
    </div>

    <!-- No account selected -->
    <div v-else-if="!transactionStore.hasTransactions && !transactionStore.loading" class="bg-white shadow rounded-lg p-6 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
      </svg>
      <h3 class="mt-2 text-lg font-medium text-gray-900">No transactions found</h3>
      <p class="mt-1 text-gray-500">Connect an account to see your transactions</p>
      <div class="mt-6">
        <router-link to="/" class="btn btn-primary">
          Go to Dashboard
        </router-link>
      </div>
    </div>

    <!-- Transaction filters and list -->
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
      
      <!-- Search and filter -->
      <div class="bg-white shadow rounded-lg p-4 mb-6">
        <div class="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
          <div class="flex-grow">
            <label for="search" class="form-label">Search Transactions</label>
            <input 
              type="text" 
              id="search" 
              v-model="searchQuery" 
              placeholder="Search by description or category" 
              class="input"
              @input="filterTransactions"
            >
          </div>
          
          <div class="w-full md:w-1/4">
            <label for="account-filter" class="form-label">Filter By Account</label>
            <select id="account-filter" v-model="selectedAccountId" class="input" @change="filterByAccount">
              <option value="">All Accounts</option>
              <optgroup v-for="institution in bankStore.institutions" :key="institution.institution_name" 
                       :label="institution.institution_name">
                <option v-for="account in getAccountsByInstitution(institution.institution_name)" 
                       :key="account.id" :value="account.id">
                  {{ account.name }} ({{ account.last_four }})
                </option>
              </optgroup>
            </select>
          </div>
          
          <div class="w-full md:w-1/4">
            <label for="filter" class="form-label">Filter By Type</label>
            <select id="filter" v-model="filterType" class="input" @change="applyFilters">
              <option value="all">All Transactions</option>
              <option value="income">Income Only</option>
              <option value="expense">Expenses Only</option>
              <option value="uncategorized">Uncategorized</option>
            </select>
          </div>
        </div>
      </div>
      
      <!-- Transaction list -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div v-if="filteredTransactions.length === 0" class="text-center py-8 text-gray-500">
          No transactions match your filters
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
              <tr v-for="transaction in filteredTransactions" :key="transaction.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ new Date(transaction.date).toLocaleDateString() }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-900">
                  {{ transaction.description }}
                  <div class="text-xs text-gray-500 mt-1">
                    {{ getAccountName(transaction.account_id) }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div class="relative">
                    <button 
                      @click="openCategoryMenu(transaction)"
                      class="px-3 py-1 rounded-full text-xs font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                      :class="getCategoryClasses(transaction.category)"
                    >
                      {{ transaction.category || 'Uncategorized' }}
                    </button>
                    
                    <!-- Dropdown menu -->
                    <div v-if="activeCategoryMenu === transaction.id" 
                         class="absolute z-10 mt-1 w-56 bg-white shadow-lg rounded-md py-1 overflow-auto max-h-60 ring-1 ring-black ring-opacity-5 focus:outline-none">
                      <div class="px-3 py-2 text-xs uppercase font-semibold text-gray-500">
                        Select Category
                      </div>
                      <hr>
                      <button 
                        v-for="category in transactionStore.categories" 
                        :key="category.id"
                        @click="updateCategory(transaction, category.name)"
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        {{ category.name }}
                      </button>
                    </div>
                  </div>
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
import { ref, computed, onMounted, nextTick, onBeforeUnmount, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useBankStore } from '../stores/bankStore';
import { useTransactionStore } from '../stores/transactionStore';

const router = useRouter();
const bankStore = useBankStore();
const transactionStore = useTransactionStore();

const searchQuery = ref('');
const filterType = ref('all');
const activeCategoryMenu = ref(null);
const selectedAccountId = ref('');

// Get all transactions from all accounts
async function fetchAllTransactions() {
  transactionStore.reset();
  if (bankStore.hasInstitutions) {
    for (const institution of bankStore.institutions) {
      // First get all accounts for this institution
      const accounts = await apiService.listAccounts(institution.institution_name);
      
      // Then fetch transactions for each account
      for (const account of accounts) {
        const transactions = await apiService.listTransactions(account.id, institution.institution_name);
        transactionStore.addTransactions(transactions);
      }
    }
  }
}

// Filter transactions based on search query and filter type
const filteredTransactions = computed(() => {
  let filtered = [];
  
  // First, filter by month
  const monthTransactions = transactionStore.currentMonthTransactions;
  
  // Then filter by account if selected
  if (selectedAccountId.value) {
    filtered = monthTransactions.filter(tx => tx.account_id === selectedAccountId.value);
  } else {
    filtered = monthTransactions;
  }
  
  // Then filter by type (income/expense)
  if (filterType.value === 'income') {
    filtered = filtered.filter(tx => parseFloat(tx.amount) > 0);
  } else if (filterType.value === 'expense') {
    filtered = filtered.filter(tx => parseFloat(tx.amount) < 0);
  } else if (filterType.value === 'uncategorized') {
    filtered = filtered.filter(tx => !tx.category || tx.category === 'Uncategorized');
  }
  
  // Then filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(tx => 
      tx.description.toLowerCase().includes(query) || 
      (tx.category && tx.category.toLowerCase().includes(query))
    );
  }
  
  // Sort by date, most recent first
  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
});

// Filter transactions when search or filter changes
function filterTransactions() {
  transactionStore.filterTransactions(searchQuery.value);
}

function applyFilters() {
  // This is handled by the computed property
}

function filterByAccount() {
  if (selectedAccountId.value) {
    const account = getAllAccounts().find(acc => acc.id === selectedAccountId.value);
    if (account) {
      bankStore.selectAccount(account);
    }
  } else {
    bankStore.selectAccount(null);
  }
}

function clearAccountFilter() {
  selectedAccountId.value = '';
  bankStore.selectAccount(null);
}

// Helper function to get account name for display
function getAccountName(accountId) {
  const allAccounts = getAllAccounts();
  const account = allAccounts.find(acc => acc.id === accountId);
  if (account) {
    const institution = bankStore.institutions.find(
      inst => inst.institution_name === account.institution?.name
    );
    return `${account.institution?.name || 'Unknown'} - ${account.name} (${account.last_four})`;
  }
  return 'Unknown Account';
}

// Helper function to get accounts by institution
function getAccountsByInstitution(institutionName) {
  return getAllAccounts().filter(
    account => account.institution?.name === institutionName
  );
}

// Helper function to get all accounts across all institutions
function getAllAccounts() {
  if (!bankStore._allAccounts) {
    bankStore._allAccounts = [];
  }
  return bankStore._allAccounts;
}

// Category dropdown management
function openCategoryMenu(transaction) {
  if (activeCategoryMenu.value === transaction.id) {
    activeCategoryMenu.value = null;
  } else {
    activeCategoryMenu.value = transaction.id;
  }
}

// Update category for a transaction
async function updateCategory(transaction, categoryName) {
  await transactionStore.categorizeTransaction(transaction.id, categoryName);
  activeCategoryMenu.value = null;
}

// Get CSS classes for category badge
function getCategoryClasses(categoryName) {
  if (!categoryName || categoryName === 'Uncategorized') {
    return 'bg-gray-100 text-gray-800';
  }
  
  const category = transactionStore.categories.find(c => c.name === categoryName);
  if (category && category.color) {
    // Create a lighter background with the category color
    return `bg-opacity-20 text-gray-800` ;
  }
  
  return 'bg-primary-100 text-primary-800';
}

// Export transactions to Google Sheets
async function exportTransactions() {
  try {
    await transactionStore.exportTransactions();
    alert('Transactions exported to Google Sheets successfully!');
  } catch (error) {
    console.error('Export failed:', error);
    alert('Failed to export transactions. Please try again.');
  }
}

// Close dropdown when clicking outside
function handleClickOutside(event) {
  if (activeCategoryMenu.value && !event.target.closest('.relative')) {
    activeCategoryMenu.value = null;
  }
}

onMounted(async () => {
  await transactionStore.fetchCategories();
  
  if (bankStore.hasInstitutions) {
    if (bankStore.selectedAccount) {
      // If a specific account is selected, just load transactions for that account
      selectedAccountId.value = bankStore.selectedAccount.id;
      await transactionStore.fetchTransactions(bankStore.selectedAccount.id, bankStore.selectedInstitution);
    } else {
      // Otherwise, load all transactions from all accounts
      await fetchAllTransactions();
    }
  } else {
    router.push('/');
  }
  
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});

// Watch for changes in selected account
watch(
  () => bankStore.selectedAccount,
  (newValue) => {
    if (newValue) {
      transactionStore.fetchTransactions(newValue.id, bankStore.selectedInstitution);
    }
  }
);
</script>