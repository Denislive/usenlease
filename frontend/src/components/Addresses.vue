<template>
  <form @submit.prevent="submitForm">
    <h3 class="text-2xl font-semibold text-gray-800 mb-4">Payment Method</h3>

    <!-- Payment Method Selection -->
    <div class="mt-4">
      <label class="block text-gray-700">
        Payment Method <span class="text-red-500">*</span>
      </label>
      <select v-model="paymentMethod" required
        class="w-full p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]">
        <option value="">Select Payment Method</option>
        <option value="stripe">Stripe</option>
        <option value="paypal">PayPal</option>
      </select>
    </div>

    <!-- Submit Button -->
    <button type="submit" class="mt-4 bg-[#1c1c1c] text-white py-2 px-4 rounded hover:text-[#ffc107]">
      Checkout
    </button>
  </form>
</template>

<script setup>
// Import necessary Vue and external dependencies
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useCartStore } from '@/store/cart';
import useNotifications from '@/store/notification';


// Define constants
const api_base_url = import.meta.env.VITE_API_BASE_URL;
const { showNotification } = useNotifications();


// Reactive state for the selected payment method
const paymentMethod = ref('');

// Router and store references
const router = useRouter();
const cartStore = useCartStore();

// Form submission handler
const submitForm = async () => {
  try {
    // Construct the payload with the selected payment method
    const payload = { paymentMethod: paymentMethod.value };

    // Handle PayPal payment (currently a placeholder)
    const handlePaypal = (response) => {
      // Alert the user that PayPal is coming soon
      showNotification('Payment Method', 'Coming Soon! Try another method!!', 'info');

      // Redirect back to the current page immediately
      router.push({ path: router.currentRoute.value.fullPath });
    };

    // Determine the payment method and proceed accordingly
    if (paymentMethod.value === 'stripe') {
      // Send request to the backend to create a Stripe checkout session
      const response = await axios.post(
        `${api_base_url}/api/create-checkout-session/`,
        payload,
        { withCredentials: true }
      );
      // Redirect the user to the Stripe checkout page
      window.location.href = response.data.url;
    } else if (paymentMethod.value === 'paypal') {
      // Placeholder logic for PayPal
      handlePaypal();
    }
  } catch (error) {
    // Handle any errors that occur during the form submission
    showNotification('Checkout error', `Checkout Error: ${error.response?.data || error.message}!`, 'error');
  }
};
</script>

<style scoped>
/* Scoped styles for the form */
</style>
