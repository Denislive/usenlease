<template>
    <header class="sticky top-0 z-50 bg-white shadow-sm p-3 sm:p-4 flex justify-between items-center border-b border-gray-100">
      <div class="flex items-center space-x-4">
        <!-- Mobile menu button -->
        <button @click="toggleSidebar" class="md:hidden text-gray-600 hover:text-gray-900">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        
        <!-- Page title -->
        <h1 class="text-lg sm:text-xl font-semibold text-gray-800 capitalize">
          {{ formattedRouteName }}
        </h1>
      </div>
  
      <!-- User info and logout -->
      <div class="flex items-center space-x-3 sm:space-x-4">
        <span class="text-sm sm:text-base text-gray-600">
          {{ authStore.user ? `Welcome, ${authStore.user.first_name}` : 'Welcome back' }}
        </span>
        <button 
          v-if="authStore.user" 
          @click="logout" 
          class="text-sm sm:text-base text-red-500 hover:text-red-700 transition-colors flex items-center"
        >
          <svg class="w-4 h-4 sm:w-5 sm:h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Logout
        </button>
      </div>
    </header>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useAuthStore } from '../store/auth';
  
  const route = useRoute();
  const router = useRouter();
  const authStore = useAuthStore();
  
  const formattedRouteName = computed(() => {
    const name = route.matched.find((r) => r.name)?.name || 'Dashboard';
    // Convert camelCase to space-separated words
    return name.replace(/([A-Z])/g, ' $1').trim();
  });
  
  const toggleSidebar = () => {
    const event = new CustomEvent('toggle-sidebar');
    window.dispatchEvent(event);
  };
  
  const logout = () => {
    authStore.logout();
    router.push('/login');
  };
  </script>