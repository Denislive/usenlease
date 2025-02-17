<template>
  <div class="flex items-center justify-center md:h-screen bg-gray-100 p-4">
    <div class="bg-white shadow-md rounded-lg sm:p-2 p-8 w-full max-w-sm">
      <div class="flex justify-center items-center">
        <img src="../assets/images/logo.jpeg" alt="logo" class="h-30 w-40">
      </div>
      <h2 class="text-2xl font-bold text-center my-6">Login</h2>

      <!-- Display server error message if login fails -->
      <div v-if="localLoginError" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4"
        role="alert">
        <i class="pi pi-exclamation-triangle mr-2"></i>
        <span class="block sm:inline">{{ localLoginError }}</span>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-4 relative">
          <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
          <input type="email" id="email" v-model="email" placeholder="user@email.com" @input="validateEmail" required
            :class="[
              'mt-1 block w-full border rounded-md p-2 focus:outline-none',
              emailError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]'
            ]" />
          <p v-if="emailError" class="absolute text-red-500 text-sm mt-1">{{ emailError }}</p>
        </div>

        <div class="mb-6 relative">
          <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
          <input type="password" id="password" placeholder="password" v-model="password" @input="validatePassword"
            required :class="[
              'mt-1 block w-full border rounded-md p-2 focus:outline-none',
              passwordError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]'
            ]" />
          <p v-if="passwordError" class="absolute text-red-500 text-sm mt-1">{{ passwordError }}</p>
        </div>

        <button type="submit" :class="[
          'w-full rounded-md py-2 transition duration-200',
          emailError || passwordError ? 'bg-red-500 text-white' : 'bg-[#1c1c1c] text-white'
        ]">
          Login
        </button>
      </form>
      <p class="mt-4 text-center text-sm">Forgot Password?<router-link to="/password-reset-request"
          class="text-[#ffc107] font-bold hover:underline"> Reset</router-link></p>

      <p class="mt-4 text-center text-sm font-bold">
        Don't have an account?
        <RouterLink :to="{ name: 'signup' }" class="text-[#ffc107] hover:underline">Sign up</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
// Login.vue
import { ref, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import { useCartStore } from '@/store/cart';
import useNotifications from '@/store/notification';
const { showNotification } = useNotifications();


const email = ref('');
const password = ref('');
const emailError = ref('');
const passwordError = ref('');
const authStore = useAuthStore();
const cartStore = useCartStore();
const localLoginError = ref(''); // Local reactive error reference
const router = useRouter();

// Watch for changes in the store's loginError and update localLoginError
watch(
  () => authStore.loginError,
  (newError) => {
    localLoginError.value = newError;
  }
);

const validateEmail = () => {
  emailError.value = /\S+@\S+\.\S+/.test(email.value) ? '' : 'Please enter a valid email address.';
};

const validatePassword = () => {
  passwordError.value = password.value.length >= 12 ? '' : 'Password must be at least 12 characters long.';
};

const handleLogin = async () => {
  localLoginError.value = ''; // Clear previous errors
  if (!emailError.value && !passwordError.value) {
    await cartStore.loadCart();
    await authStore.login(email.value, password.value, cartStore.cart);
  }
};


</script>
