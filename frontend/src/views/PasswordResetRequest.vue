<template>
    <div class="flex items-center justify-center min-h-screen bg-gold">
      <div class="bg-white shadow-md rounded-lg p-8 w-full max-w-md">
        <h2 class="text-2xl font-bold text-center text-dark mb-6">Reset Password</h2>
        <form @submit.prevent="requestPasswordReset">
          <div class="mb-4">
            <label for="email" class="block text-sm font-medium text-dark">Email Address</label>
            <input
              type="email"
              id="email"
              v-model="email"
              required
              class="mt-1 block w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#ffc107]"
              placeholder="Enter your email"
            />
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-[#1c1c1c] text-[#ffc107] font-medium py-2 rounded-md  focus:ring-2 focus:ring-dark focus:outline-none disabled:opacity-50"
          >
            {{ loading ? "Sending..." : "Request Reset Link" }}
          </button>
         
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import { ref } from "vue";
  import { useRouter } from "vue-router";

  import useNotifications from '@/store/notification';

  
  export default {
    setup() {
      const email = ref("");
      const loading = ref(false);
      const api_base_url = import.meta.env.VITE_API_BASE_URL;
      const { showNotification } = useNotifications();

      const router = useRouter();


    
      const requestPasswordReset = async () => {
        loading.value = true;
        
  
        try {
          const response = await axios.post(
            `${api_base_url}/api/accounts/password-reset/send_reset_email/`,
            { email: email.value }
          );
          router.push({ name: 'home' });
          showNotification('Password Reset Request', `${response.data.message}` || "Reset link sent successfully!", 'success');

        } catch (err) {
          showNotification('Password Reset Request', `${err.response?.data?.error}` || "Failed to send reset link. Please try again.", 'error');

        } finally {
          loading.value = false;
        }
      };
  
      return {
        email,
        loading,  
        requestPasswordReset,
      };
    },
  };
  </script>
  
  <style scoped>
  /* Add additional styling if necessary */
  </style>
  