<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Accounts</h1>
      <div>
        <router-link to="/" class="btn btn-outline mr-2">
          Back to Dashboard
        </router-link>
        <TellerConnect />
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading accounts...</p>
    </div>

    <!-- Error message -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">
            {{ error }}
          </p>
        </div>
      </div>
    </div>

    <!-- No accounts connected yet -->
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

    <!-- Account list grouped by institution -->
    <div v-else>
      <div v-for="institution in bankStore.institutions" :key="institution.institution_name" class="mb-8">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold text-gray-900">
            {{ institution.institution_name }}
          </h2>
          <button @click="disconnectBank(institution.institution_name)" class="btn btn-danger btn-sm">
            Disconnect
          </button>
        </div>
        
        <div v-if="!getAccountsForInstitution(institution.institution_name).length" class="bg-white shadow rounded-lg p-6 text-center">
          <p class="text-gray-500">No accounts found for this institution</p>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="account in getAccountsForInstitution(institution.institution_name)" :key="account.id" 
               class="bg-white shadow rounded-lg overflow-hidden">
            <div class="px-6 py-5 border-b border-gray-200">
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-medium text-gray-900">{{ account.name }}</h3>
                <span class="px-2 py-1 rounded-full text-xs font-medium" 
                     :class="getAccountTypeClasses(account.type, account.subtype)">
                  {{ formatAccountType(account.type, account.subtype) }}
                </span>
              </div>
              <p class="text-sm text-gray-500 mt-1">
                Account ending in {{ account.last_four }}
              </p>
            </div>
            
            <div class="px-6 py-5 flex justify-between items-center bg-gray-50">
              <div>
                <p class="text-sm text-gray-500">Balance</p>
                <p class="text-xl font-semibold text-gray-900">
                  {{ account.currency }} {{ account.balance || '••••' }}
                </p>
              </div>
              <div>
                <button @click="viewTransactions(account, institution.institution_name)" class="btn btn-primary text-sm">
                  View Transactions
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useBankStore } from '../stores/bankStore';
import { useTransactionStore } from '../stores/transactionStore';
import TellerConnect from '../components/accounts/TellerConnect.vue';
import { apiService } from '../services/api';

const router = useRouter();
const bankStore = useBankStore();
const transactionStore = useTransactionStore();
const allAccounts = ref([]);
const loading = ref(false);
const error = ref(null);

// Format account type and subtype for display
function formatAccountType(type, subtype) {
  if (subtype) {
    // Convert snake_case to Title Case
    const formattedSubtype = subtype
      .replace(/_/g, ' ')
      .replace(/\w\S*/g, word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());
    
    return formattedSubtype;
  }
  return type.charAt(0).toUpperCase() + type.slice(1);
}

// Get CSS classes for account type badge
function getAccountTypeClasses(type, subtype) {
  let baseClasses = 'bg-opacity-20';
  
  if (type === 'depository') {
    return `${baseClasses} bg-primary-500 text-primary-800`;
  } else if (type === 'credit') {
    return `${baseClasses} bg-red-500 text-red-800`;
  } else if (type === 'investment') {
    return `${baseClasses} bg-green-500 text-green-800`;
  } else if (type === 'loan') {
    return `${baseClasses} bg-yellow-500 text-yellow-800`;
  }
  
  return `${baseClasses} bg-gray-500 text-gray-800`;
}

// Function to get accounts for a specific institution
function getAccountsForInstitution(institutionName) {
  return allAccounts.value.filter(account => 
    account.institution && account.institution.name === institutionName
  );
}

// Function to view transactions for a specific account
async function viewTransactions(account, institutionName) {
  bankStore.selectAccount(account);
  bankStore.selectedInstitution = institutionName;
  await transactionStore.fetchTransactions(account.id, institutionName);
  router.push('/transactions');
}

// Function to disconnect a bank
async function disconnectBank(institutionName) {
  if (confirm(`Are you sure you want to disconnect ${institutionName}?`)) {
    await bankStore.disconnectInstitution(institutionName);
    await loadAllAccounts();
  }
}

// Load all accounts from all institutions
async function loadAllAccounts() {
  loading.value = true;
  error.value = null;
  allAccounts.value = [];
  bankStore._allAccounts = [];
  
  if (bankStore.hasInstitutions) {
    for (const institution of bankStore.institutions) {
      try {
        const accounts = await apiService.listAccounts(institution.institution_name);
        
        // Add institution info to each account if not already present
        accounts.forEach(account => {
          if (!account.institution) {
            account.institution = {
              name: institution.institution_name,
              id: institution.institution_id
            };
          }
          
          // Try to get balance information
          if (account.links && account.links.balances) {
            apiService.getBalance(account.id, institution.institution_name)
              .then(balanceInfo => {
                account.balance = balanceInfo.available || balanceInfo.ledger;
              })
              .catch(() => {
                account.balance = null;
              });
          }
        });
        
        allAccounts.value = [...allAccounts.value, ...accounts];
        bankStore._allAccounts = [...bankStore._allAccounts, ...accounts];
      } catch (err) {
        console.error(`Error loading accounts for ${institution.institution_name}:`, err);
        error.value = `Failed to load accounts for ${institution.institution_name}`;
      }
    }
  }
  
  loading.value = false;
}

onMounted(async () => {
  await bankStore.fetchInstitutions();
  await loadAllAccounts();
});
</script>