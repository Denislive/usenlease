<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useCartStore } from '@/store/cart';
import useNotifications from '@/store/notification';

// Constants at the top for better visibility
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const PAYMENT_METHODS = {
  STRIPE: 'stripe',
  PAYPAL: 'paypal'
};

// Composables
const { showNotification } = useNotifications();
const router = useRouter();
const cartStore = useCartStore();

// Reactive state
const paymentMethod = ref('');
const loading = ref(false);
const error = ref(null);

/**
 * Validates the selected payment method
 * @returns {boolean} True if valid, false otherwise
 */
const validatePaymentMethod = () => {
  if (!paymentMethod.value) {
    showNotification(
      'Payment Required',
      'Please select a payment method to continue',
      'warning'
    );
    return false;
  }
  return true;
};

/**
 * Handles PayPal payment method selection
 */
const handlePayPalPayment = async () => {
  showNotification(
    'Payment Method', 
    'Coming Soon! Please try another method.', 
    'info'
  );
  
  try {
    await router.push({ path: router.currentRoute.value.fullPath });
  } catch (routerError) {
    error.value = 'Failed to refresh page. Please try again.';
  }
};

/**
 * Handles Stripe payment processing
 */
const handleStripePayment = async () => {
  try {
    const payload = { 
      paymentMethod: paymentMethod.value,
      // Consider adding cart/order details if needed
    };

    const response = await axios.post(
      `${API_BASE_URL}/api/create-checkout-session/`,
      payload,
      { 
        withCredentials: true,
        timeout: 10000, // 10 second timeout
        headers: {
          'Content-Type': 'application/json',
          // Add any auth headers if required
        }
      }
    );

    if (!response?.data?.url) {
      throw new Error('Invalid response: Missing redirect URL.');
    }

    // Security consideration for redirects
    if (typeof response.data.url === 'string' && 
        response.data.url.startsWith('https')) {
      window.location.href = response.data.url;
    } else {
      throw new Error('Invalid redirect URL provided.');
    }
  } catch (err) {
    throw err; // Re-throw for centralized error handling
  }
};

/**
 * Main form submission handler
 */
const submitForm = async () => {
  if (loading.value) return;
  
  // Reset error state
  error.value = null;
  loading.value = true;

  try {
    // Validate input
    if (!validatePaymentMethod()) {
      loading.value = false;
      return;
    }

    // Route to appropriate payment handler
    switch (paymentMethod.value) {
      case PAYMENT_METHODS.PAYPAL:
        await handlePayPalPayment();
        break;
      case PAYMENT_METHODS.STRIPE:
        await handleStripePayment();
        break;
      default:
        throw new Error('Unsupported payment method selected');
    }
  } catch (err) {
    error.value = err;

    let userMessage = 'Something went wrong. Please try again later.';
    
    // Enhanced error handling
    if (err.response) {
      // API error response
      const { status, data } = err.response;
      
      if (status === 401) {
        userMessage = 'Session expired. Please login again.';
      } else if (status === 403) {
        userMessage = 'Unauthorized action. Please verify your details.';
      } else if (status === 429) {
        userMessage = 'Too many requests. Please wait and try again.';
      } else if (data?.message) {
        userMessage = data.message;
      } else {
        userMessage = `Payment processing failed (${status}).`;
      }
    } else if (err.request) {
      // Network error
      userMessage = 'Network error. Please check your connection.';
    } else if (err.message) {
      // Client-side error
      userMessage = err.message;
    }

    showNotification('Payment Error', userMessage, 'error');
  } finally {
    loading.value = false;
  }
};

/**
 * Selects payment method with validation
 * @param {string} method - The payment method to select
 */
const selectPaymentMethod = (method) => {
  if (Object.values(PAYMENT_METHODS).includes(method)) {
    paymentMethod.value = method;
    error.value = null; // Clear error when method changes
  }
};
</script>

<template>
  <div class="max-w-lg mx-auto p-6 bg-white shadow-lg rounded-lg">
    <form @submit.prevent="submitForm" class="payment-form">
      <h3 class="text-2xl font-semibold text-gray-800 mb-6">
        Choose Payment Method
      </h3>

      <!-- Payment Method Selection -->
      <div class="flex gap-6 justify-center mb-6 relative">
        <!-- Stripe Option -->
        <div 
          @click="selectPaymentMethod(PAYMENT_METHODS.STRIPE)" 
          :class="{
            'border-2 border-[#1c1c1c]': paymentMethod === PAYMENT_METHODS.STRIPE,
            'hover:bg-[#2c2c2c]': !loading
          }"
          class="p-6 cursor-pointer rounded-lg bg-[#1c1c1c] transition-all transform hover:scale-105 active:scale-95 flex items-center justify-center shadow-md relative"
          :disabled="loading"
          aria-label="Pay with Stripe"
          role="button"
          tabindex="0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" class="w-12 h-12">
            <path fill="#ffc100" d="M165 144.7l-43.3 9.2.2 142.4c0 26.3 19.8 43.3 46.1 43.3 14.6 0 25.3-2.7 31.2-5.9v-33.8c-5.7 2.3-33.7 10.5-33.7-15.7V221h33.7v-37.8h-33.7zm89.1 51.6l-2.7-13.1H213v153.2h44.3V233.3c10.5-13.8 28.2-11.1 33.9-9.3v-40.8c-6-2.1-26.7-6-37.1 13.1zm92.3-72.3l-44.6 9.5v36.2l44.6-9.5zM44.9 228.3c0-6.9 5.8-9.6 15.1-9.7 13.5 0 30.7 4.1 44.2 11.4v-41.8c-14.7-5.8-29.4-8.1-44.1-8.1-36 0-60 18.8-60 50.2 0 49.2 67.5 41.2 67.5 62.4 0 8.2-7.1 10.9-17 10.9-14.7 0-33.7-6.1-48.6-14.2v40c16.5 7.1 33.2 10.1 48.5 10.1 36.9 0 62.3-15.8 62.3-47.8 0-52.9-67.9-43.4-67.9-63.4zM640 261.6c0-45.5-22-81.4-64.2-81.4s-67.9 35.9-67.9 81.1c0 53.5 30.3 78.2 73.5 78.2 21.2 0 37.1-4.8 49.2-11.5v-33.4c-12.1 6.1-26 9.8-43.6 9.8-17.3 0-32.5-6.1-34.5-26.9h86.9c.2-2.3 .6-11.6 .6-15.9zm-87.9-16.8c0-20 12.3-28.4 23.4-28.4 10.9 0 22.5 8.4 22.5 28.4zm-112.9-64.6c-17.4 0-28.6 8.2-34.8 13.9l-2.3-11H363v204.8l44.4-9.4 .1-50.2c6.4 4.7 15.9 11.2 31.4 11.2 31.8 0 60.8-23.2 60.8-79.6 .1-51.6-29.3-79.7-60.5-79.7zm-10.6 122.5c-10.4 0-16.6-3.8-20.9-8.4l-.3-66c4.6-5.1 11-8.8 21.2-8.8 16.2 0 27.4 18.2 27.4 41.4 .1 23.9-10.9 41.8-27.4 41.8zm-126.7 33.7h44.6V183.2h-44.6z"/>
          </svg>

          <span 
            v-if="paymentMethod === PAYMENT_METHODS.STRIPE" 
            class="absolute top-0 right-0 text-green-500 rounded-full p-1"
            aria-hidden="true"
          >
            <i class="pi pi-verified text-lg"></i>
          </span>
        </div>

        <!-- PayPal Option -->
        <div 
          @click="selectPaymentMethod(PAYMENT_METHODS.PAYPAL)" 
          :class="{
            'border-2 border-[#1c1c1c]': paymentMethod === PAYMENT_METHODS.PAYPAL,
            'hover:bg-[#2c2c2c]': !loading
          }"
          class="p-6 cursor-pointer rounded-lg bg-[#1c1c1c] transition-all transform hover:scale-105 active:scale-95 flex items-center justify-center shadow-md relative"
          :disabled="loading"
          aria-label="Pay with PayPal"
          role="button"
          tabindex="0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" class="w-12 h-12">
            <path fill="#ffc100" d="M111.4 295.9c-3.5 19.2-17.4 108.7-21.5 134-.3 1.8-1 2.5-3 2.5H12.3c-7.6 0-13.1-6.6-12.1-13.9L58.8 46.6c1.5-9.6 10.1-16.9 20-16.9 152.3 0 165.1-3.7 204 11.4 60.1 23.3 65.6 79.5 44 140.3-21.5 62.6-72.5 89.5-140.1 90.3-43.4 .7-69.5-7-75.3 24.2zM357.1 152c-1.8-1.3-2.5-1.8-3 1.3-2 11.4-5.1 22.5-8.8 33.6-39.9 113.8-150.5 103.9-204.5 103.9-6.1 0-10.1 3.3-10.9 9.4-22.6 140.4-27.1 169.7-27.1 169.7-1 7.1 3.5 12.9 10.6 12.9h63.5c8.6 0 15.7-6.3 17.4-14.9 .7-5.4-1.1 6.1 14.4-91.3 4.6-22 14.3-19.7 29.3-19.7 71 0 126.4-28.8 142.9-112.3 6.5-34.8 4.6-71.4-23.8-92.6z"/>
          </svg>

          <span 
            v-if="paymentMethod === PAYMENT_METHODS.PAYPAL" 
            class="absolute top-0 right-0 text-green-500 rounded-full p-1"
            aria-hidden="true"
          >
            <i class="pi pi-verified text-lg"></i>
          </span>
        </div>
      </div>

      <!-- Error Message (if any) -->
      <div 
        v-if="error" 
        class="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm"
        role="alert"
      >
        <i class="pi pi-exclamation-circle mr-2"></i>
        {{ error.message || error }}
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="loading || !paymentMethod"
        class="w-full mt-6 bg-[#1c1c1c] text-white py-3 rounded-lg text-lg font-semibold transition duration-200 ease-in-out flex items-center justify-center"
        :class="{
          'hover:bg-[#2c2c2c]': !loading && paymentMethod,
          'opacity-50 cursor-not-allowed': loading || !paymentMethod
        }"
        aria-live="polite"
      >
        <template v-if="loading">
          <i class="pi pi-spinner pi-spin mr-2"></i>
          Processing Payment...
        </template>
        <template v-else>
          Proceed to Checkout
        </template>
      </button>
    </form>
  </div>
</template>

<style scoped>
/* REMOVED the [disabled] styles that were affecting the payment methods */
.payment-form {
  @apply space-y-4;
}

/* Only apply disabled styles to actual buttons */
button:disabled {
  @apply opacity-50 cursor-not-allowed;
  pointer-events: none;
}

/* Focus styles remain */
[role="button"]:focus {
  @apply outline-none ring-2 ring-offset-2 ring-[#1c1c1c];
}

button:focus {
  @apply outline-none ring-2 ring-offset-2 ring-[#1c1c1c];
}
</style>