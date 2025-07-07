<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100 p-4">
    <div class="bg-white shadow-md rounded-lg p-6 sm:p-8 w-full max-w-sm">
      <div class="flex justify-center items-center mb-6">
        <img src="../assets/images/logo.jpeg" alt="Company Logo" class="h-30 w-40" loading="lazy" width="160"
          height="120">
      </div>
      <h1 class="text-2xl font-bold text-center mb-6">Login to Your Account</h1>

      <!-- Error Message -->
      <div v-if="localLoginError" class="bg-red-50 border-l-4 border-red-500 p-4 mb-4 flex items-start" role="alert"
        aria-live="assertive">
        <i class="pi pi-exclamation-triangle text-red-500 mr-2 mt-0.5"></i>
        <div>
          <p class="text-red-700 font-medium">Login Error</p>
          <p class="text-red-600 text-sm">{{ localLoginError }}</p>
        </div>
      </div>

      <form @submit.prevent="handleLogin" novalidate>
        <!-- Email Field -->
        <div class="mb-4">
          <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
            Email Address
            <span class="text-red-500">*</span>
          </label>
          <input type="email" id="email" v-model.trim="email" @input="validateEmail" @blur="validateEmail"
            placeholder="user@example.com" required autocomplete="email" :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1',
              emailError ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:border-[#1c1c1c] focus:ring-[#1c1c1c]'
            ]" aria-describedby="email-error" />
          <p v-if="emailError" id="email-error" class="mt-1 text-sm text-red-600">
            {{ emailError }}
          </p>
        </div>

        <!-- Password Field -->
        <div class="mb-6">
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
            Password
            <span class="text-red-500">*</span>
          </label>
          <input type="password" id="password" v-model.trim="password" @input="validatePassword"
            @blur="validatePassword" placeholder="••••••••" required minlength="12" autocomplete="current-password"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1',
              passwordError ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:border-[#1c1c1c] focus:ring-[#1c1c1c]'
            ]" aria-describedby="password-error" />
          <p v-if="passwordError" id="password-error" class="mt-1 text-sm text-red-600">
            {{ passwordError }}
          </p>
        </div>

        <!-- Submit Button -->
        <button type="submit" :disabled="loading" :class="[
          'w-full py-2.5 px-4 rounded-md font-medium transition-colors duration-200 flex items-center justify-center',
          loading || emailError || passwordError
            ? 'bg-gray-400 text-white cursor-not-allowed'
            : 'bg-[#1c1c1c] text-white hover:bg-gray-800 focus:ring-2 focus:ring-[#1c1c1c] focus:ring-offset-2'
        ]" aria-live="polite">
          <i v-if="loading" class="pi pi-spinner pi-spin mr-2"></i>
          <span>{{ loading ? 'Authenticating...' : 'Login' }}</span>
        </button>
      </form>

      <!-- Links Section -->
      <div class="mt-6 space-y-3 text-center">
        <p class="text-sm">
          <router-link to="/password-reset-request"
            class="text-[#ffc107] font-semibold hover:underline focus:outline-none focus:underline">
            Forgot Password?
          </router-link>
        </p>
        <p class="text-sm font-semibold">
          Don't have an account?
          <router-link :to="{ name: 'signup' }"
            class="text-[#ffc107] hover:underline focus:outline-none focus:underline">
            Sign up
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import { useCartStore } from '@/store/cart';
import useNotifications from '@/store/notification';

// Constants
const MIN_PASSWORD_LENGTH = 8;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Stores and Services
const { showNotification } = useNotifications();
const authStore = useAuthStore();
const cartStore = useCartStore();
const router = useRouter();

// Reactive State
const email = ref('');
const password = ref('');
const emailError = ref('');
const passwordError = ref('');
const localLoginError = ref('');
const loading = ref(false);



// Validation Functions
const validateEmail = () => {
  if (!email.value) {
    emailError.value = 'Email is required';
  } else if (!EMAIL_REGEX.test(email.value)) {
    emailError.value = 'Please enter a valid email address';
  } else {
    emailError.value = '';
  }
};

const validatePassword = () => {
  if (!password.value) {
    passwordError.value = 'Password is required';
  } else if (password.value.length < MIN_PASSWORD_LENGTH) {
    passwordError.value = `Password must be at least ${MIN_PASSWORD_LENGTH} characters`;
  } else {
    passwordError.value = '';
  }
};

// Form Submission
const handleLogin = async () => {
  // Validate before submission
  validateEmail();
  validatePassword();

  if (emailError.value || passwordError.value) {
    return;
  }

  loading.value = true;
  localLoginError.value = '';

  try {
    await Promise.all([
      cartStore.loadCart(),
      authStore.login(email.value, password.value, cartStore.cart)
    ]);


    // ✅ Redirect after login
    const redirectPath = authStore.redirectTo && authStore.redirectTo !== ''
      ? authStore.redirectTo
      : { name: 'home' };

    authStore.redirectTo = ''; // Clear it after use
    router.push(redirectPath);
  } catch (error) {
    console.error('Login error:', error);
    localLoginError.value = error.message || 'Login failed. Please try again.';

    // Clear sensitive data on error
    password.value = '';
    passwordError.value = '';
  } finally {
    loading.value = false;
  }
};
</script>