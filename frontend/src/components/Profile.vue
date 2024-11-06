<template>
    <div class="max-w-3xl mx-auto p-4">
      <h1 class="text-2xl font-semibold mb-4">User Profile</h1>
      <div v-if="user" class="bg-white shadow rounded-lg p-6">
        <h2 class="text-xl font-medium mb-2">Profile Information</h2>
        <p class="mb-2"><strong>Name:</strong> {{ user.name }}</p>
        <p class="mb-2"><strong>Email:</strong> {{ user.email }}</p>
        <p class="mb-4"><strong>Joined:</strong> {{ formattedDate(user.created_at) }}</p>
        <button 
          @click="logout" 
          class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition duration-200">
          Logout
        </button>
      </div>
      <div v-else class="text-center">
        <p class="text-gray-500">Loading user information...</p>
      </div>
    </div>
  </template>
  
  <script>
  import { useAuthStore } from '@/store/auth';
  import { onMounted } from 'vue';
  
  export default {
    setup() {
      const authStore = useAuthStore();
  
      const formattedDate = (dateString) => {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
      };
  
      const logout = async () => {
        await authStore.logout();
        // Optionally redirect to home or login
        router.push({ name: 'login' });
      };
  
      return {
        user: authStore.user,
        formattedDate,
        logout,
      };
    },
    mounted() {
      // Optionally fetch user details from an API if needed
    },
  };
  </script>
  
  <style scoped>
  /* Add any component-specific styles here */
  </style>
  