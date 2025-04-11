<template>
  <div class="flex items-center justify-center min-h-screen bg-gold">
    <div class="bg-white shadow-md rounded-lg p-8 w-full max-w-md">
      <div class="flex justify-center items-center">
        <img src="../assets/images/logo.jpeg" alt="logo" class="h-30 w-40">
      </div>
      <h2 class="text-2xl font-bold text-center text-dark my-6">Set New Password</h2>
      <form @submit.prevent="resetPassword">
        <div class="mb-4">
          <label for="new-password" class="block text-sm font-medium text-dark">New Password</label>
          <input
            type="password"
            id="new-password"
            v-model="newPassword"
            required
            minlength="8"
            class="mt-1 block w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#ffc107]"
            placeholder="Enter new password (min 8 characters)"
            @input="validatePassword"
          />
          <p v-if="passwordError" class="text-red-500 text-xs mt-1">{{ passwordError }}</p>
        </div>
        <div class="mb-4">
          <label for="confirm-password" class="block text-sm font-medium text-dark">Confirm Password</label>
          <input
            type="password"
            id="confirm-password"
            v-model="confirmPassword"
            required
            minlength="8"
            class="mt-1 block w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#ffc107]"
            placeholder="Confirm your password"
            @input="validatePassword"
          />
        </div>
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-[#1c1c1c] text-[#ffc107] font-medium py-2 rounded-md disabled:opacity-50"
        >
          {{ loading ? "Resetting..." : "Reset Password" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";
import useNotifications from '@/store/notification';

export default {
  setup() {
    const newPassword = ref("");
    const confirmPassword = ref("");
    const passwordError = ref("");
    const api_base_url = import.meta.env.VITE_API_BASE_URL;
    const { showNotification } = useNotifications();

    const loading = ref(false);
    
    const route = useRoute();
    const router = useRouter();

    // Extract uidb64 and token from the route parameters
    const { uid, token } = route.query;

    const validatePassword = () => {
      if (newPassword.value.length < 8) {
        passwordError.value = "Password must be at least 8 characters long";
        return false;
      }
      
      if (newPassword.value !== confirmPassword.value) {
        passwordError.value = "Passwords do not match";
        return false;
      }
      
      passwordError.value = "";
      return true;
    };

    const resetPassword = async () => {
      if (!validatePassword()) {
        return;
      }

      loading.value = true;

      try {
        // Send password reset request to backend
        const response = await axios.post(
          `${api_base_url}/api/accounts/password-reset/confirm/${uid}/${token}/`,
          {
            new_password: newPassword.value,
            confirm_password: confirmPassword.value,
          }
        );
        router.push({ name: 'login' });
        showNotification('Password Reset', `${response.data.message}` || "Password was reset successfully!", 'success');

      } catch (err) {
        showNotification('Password Reset', `${err.response?.data?.error}` || "Failed to reset password. Please try again.", 'error');
      } finally {
        loading.value = false;
      }
    };

    return {
      newPassword,
      confirmPassword,
      passwordError,
      loading,
      resetPassword,
      validatePassword,
    };
  },
};
</script>

<style scoped>
/* Add additional styling if necessary */
</style>