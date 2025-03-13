<template>
  <nav class="bg-white shadow">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/" class="text-xl font-bold text-primary-600">
              BudgetTracker
            </router-link>
          </div>
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <router-link 
              to="/" 
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              :class="[$route.path === '/' ? 'border-primary-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700']"
            >
              Dashboard
            </router-link>
            
            <router-link 
              to="/accounts" 
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              :class="[$route.path === '/accounts' ? 'border-primary-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700']"
            >
              Accounts
            </router-link>
            
            <router-link 
              to="/transactions" 
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              :class="[$route.path === '/transactions' ? 'border-primary-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700']"
            >
              Transactions
            </router-link>
            
            <router-link 
              to="/categories" 
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              :class="[$route.path === '/categories' ? 'border-primary-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700']"
            >
              Categories
            </router-link>
          </div>
        </div>
        
        <div class="-mr-2 flex items-center sm:hidden">
          <!-- Mobile menu button -->
          <button 
            @click="mobileMenuOpen = !mobileMenuOpen" 
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
          >
            <span class="sr-only">Open main menu</span>
            <svg 
              class="h-6 w-6" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor" 
              aria-hidden="true"
              :class="{ 'hidden': mobileMenuOpen, 'block': !mobileMenuOpen }"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg 
              class="h-6 w-6" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor" 
              aria-hidden="true"
              :class="{ 'block': mobileMenuOpen, 'hidden': !mobileMenuOpen }"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div class="sm:hidden" :class="{ 'block': mobileMenuOpen, 'hidden': !mobileMenuOpen }">
      <div class="pt-2 pb-3 space-y-1">
        <router-link 
          to="/" 
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          :class="[$route.path === '/' ? 'bg-primary-50 border-primary-500 text-primary-700' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700']"
          @click="mobileMenuOpen = false"
        >
          Dashboard
        </router-link>
        
        <router-link 
          to="/accounts" 
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          :class="[$route.path === '/accounts' ? 'bg-primary-50 border-primary-500 text-primary-700' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700']"
          @click="mobileMenuOpen = false"
        >
          Accounts
        </router-link>
        
        <router-link 
          to="/transactions" 
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          :class="[$route.path === '/transactions' ? 'bg-primary-50 border-primary-500 text-primary-700' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700']"
          @click="mobileMenuOpen = false"
        >
          Transactions
        </router-link>
        
        <router-link 
          to="/categories" 
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          :class="[$route.path === '/categories' ? 'bg-primary-50 border-primary-500 text-primary-700' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700']"
          @click="mobileMenuOpen = false"
        >
          Categories
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const mobileMenuOpen = ref(false);
</script>