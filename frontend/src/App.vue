<template>
  <div class="min-h-screen bg-gray-100">
    <Navbar />
    <main class="py-6">
      <router-view />
    </main>
    <footer class="bg-white py-4 border-t border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p class="text-center text-gray-500 text-sm">
          Personal Budget Tracker &copy; {{ new Date().getFullYear() }}
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from './components/ui/Navbar.vue';
</script>