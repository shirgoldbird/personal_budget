<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Accounts</h1>
      <router-link to="/" class="btn btn-outline">
        Back to Dashboard
      </router-link>
    </div>
    
    <!-- Loading state -->
    <div v-if="bankStore.loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading accounts...</p>
    </div>

    <!-- Error message -->
    <div v-else-if="bankStore.error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">
            {{ bankStore.error }}
          </p>
        </div>
      </div>
    </div>

    <!-- No accounts selected yet -->
    <div v-else-if="!bankStore.selectedInstitution" class="bg-white shadow rounded-lg p-6 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
      </svg>
      <h3 class="mt-2 text-lg font-medium text-gray-900">No institution selected</h3>
      <p class="mt-1 text-gray-500">Please select an institution from the dashboard</p>
      <div class="mt-6">
        <router-link to="/" class="btn btn-primary">
          Go to Dashboard
        </router-link>
      </div>
    </div>

    <!-- Account list -->
    <div v-else>
      <h2 class="text-xl font-semibold text-gray-900 mb-6">
        {{ bankStore.selectedInstitution }} Accounts
      </h2>
      
      <div v-if="!bankStore.hasAccounts" class="bg-white shadow rounded-lg p-6 text-center">
        <p class="text-gray-500">No accounts found for this institution</p>
      </div>
      
      <div v-else class="grid grid-cols-1 gap-6">
        <div v-for="account in bankStore.accounts" :key="account.id" class="bg-white shadow rounded-lg overflow-hidden">
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
                {{ account.currency }} •••• 
              </p>
            </div>
            <div>
              <button @click="viewTransactions(account)" class="btn btn-primary text-sm">
                View Transactions
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useBankStore } from '../stores/bankStore';
import { useTransactionStore } from '../stores/transactionStore';

const router = useRouter();
const bankStore = useBankStore();
const transactionStore = useTransactionStore();

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

// Function to view transactions for a specific account
function viewTransactions(account) {
  bankStore.selectAccount(account);
  transactionStore.fetchTransactions(account.id, bankStore.selectedInstitution);
  router.push('/transactions');
}

onMounted(() => {
  // If no institution is selected, redirect to dashboard
  if (!bankStore.selectedInstitution && bankStore.hasInstitutions) {
    router.push('/');
  }
});

// Watch for changes in selectedInstitution
watch(
  () => bankStore.selectedInstitution,
  (newValue) => {
    if (newValue) {
      bankStore.fetchAccounts(newValue);
    }
  }
);
</script>