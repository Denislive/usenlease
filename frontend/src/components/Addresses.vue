<template>
  <form @submit.prevent="submitForm">
    <h3 class="text-2xl font-semibold text-gray-800 mb-4">Payment Method</h3>

    <!-- Payment Method -->
    <div class="mt-4">
      <label class="block text-gray-700">
        Payment Method <span class="text-red-500">*</span>
      </label>
      <select
        v-model="paymentMethod"
        required
        class="w-full p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]"
      >
        <option value="">Select Payment Method</option>
        <option value="stripe">Stripe</option>
        <option value="paypal">PayPal</option>
      </select>
    </div>

    <!-- Submit Button -->
    <button
      type="submit"
      class="mt-4 bg-[#1c1c1c] text-white py-2 px-4 rounded hover:text-[#ffc107]"
    >
      Checkout
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useCartStore } from '@/store/cart';

const api_base_url = import.meta.env.VITE_API_BASE_URL;


const paymentMethod = ref('');
const router = useRouter();
const cartStore = useCartStore();

const submitForm = async () => {
  try {
    // Construct the payload
    const payload = {
      paymentMethod: paymentMethod.value,
    };

    // Send the payload to the server with credentials
    const response = await axios.post(
      `${api_base_url}/api/create-checkout-session/`,
      payload,
      { withCredentials: true }
    );

    // Redirect to payment page (Stripe or PayPal)
    if (paymentMethod.value === 'stripe') {
      window.location.href = response.data.url;
    } else if (paymentMethod.value === 'paypal') {
      window.location.href = response.data.paypalUrl;
    }
  } catch (error) {
    // Handle errors
    console.error('Checkout error:', error.response?.data || error.message);
  }
};
</script>

<style scoped></style>
