<template>
    <form @submit.prevent="submitForm">
      <h3 class="text-2xl font-semibold text-gray-800 mb-4">Billing Details</h3>
  
      <!-- Use Default Address -->
      <div class="mb-4">
        <div class="flex items-center">
          <input id="defaultAddress" type="checkbox" v-model="useDefaultAddress" class="mr-2">
          <label for="defaultAddress" class="text-gray-700">Use saved default address</label>
        </div>
      </div>
  
      <!-- Billing Fields -->
      <div v-if="!useDefaultAddress" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-gray-700">First Name <span class="text-red-500">*</span></label>
          <input v-model="billing.firstName" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">Last Name <span class="text-red-500">*</span></label>
          <input v-model="billing.lastName" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">Company Name</label>
          <input v-model="billing.companyName" type="text" class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">Country <span class="text-red-500">*</span></label>
          <select v-model="billing.country" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]">
            <option value="">Select Country</option>
            <option value="USA">USA</option>
          </select>
        </div>
        <div>
          <label class="block text-gray-700">Street Address <span class="text-red-500">*</span></label>
          <input v-model="billing.streetAddress" placeholder="House number and street name" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <input v-model="billing.apartment" placeholder="Apartment, suite, unit etc. (optional)" type="text" class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">Town / City <span class="text-red-500">*</span></label>
          <input v-model="billing.city" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">State / County <span class="text-red-500">*</span></label>
          <input v-model="billing.state" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">Phone <span class="text-red-500">*</span></label>
          <input v-model="billing.phone" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">Email Address <span class="text-red-500">*</span></label>
          <input v-model="billing.email" type="email" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
      </div>
  
      <!-- Ship to Different Address -->
      <div class="mt-4">
        <div class="flex items-center">
          <input id="differentAddress" type="checkbox" v-model="isDifferentAddress" class="mr-2">
          <label for="differentAddress" class="text-gray-700">Ship to a different address?</label>
        </div>
      </div>
  
      <!-- Shipping Fields -->
      <div v-if="isDifferentAddress" class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <div>
          <label class="block text-gray-700">First Name <span class="text-red-500">*</span></label>
          <input v-model="shipping.firstName" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">Last Name <span class="text-red-500">*</span></label>
          <input v-model="shipping.lastName" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">Country <span class="text-red-500">*</span></label>
          <select v-model="shipping.country" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]">
            <option value="">Select Country</option>
            <option value="USA">USA</option>
          </select>
        </div>
        <div>
          <label class="block text-gray-700">Street Address <span class="text-red-500">*</span></label>
          <input v-model="shipping.streetAddress" placeholder="House number and street name" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <input v-model="shipping.apartment" placeholder="Apartment, suite, unit etc. (optional)" type="text" class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
        <div>
          <label class="block text-gray-700">Town / City <span class="text-red-500">*</span></label>
          <input v-model="shipping.city" type="text" required class="mt-1 p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
        </div>
      </div>
  
      <!-- Payment Method -->
      <div class="mt-4">
        <label class="block text-gray-700">Payment Method <span class="text-red-500">*</span></label>
        <select v-model="paymentMethod" required class="w-full p-2 border border-[#1c1c1c] rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]">
          <option value="">Select Payment Method</option>
          <option value="stripe">Stripe</option>
          <option value="paypal">PayPal</option>
        </select>
      </div>
  
      <!-- Submit Button -->
      <button type="submit" class="mt-4 bg-[#1c1c1c] text-white py-2 px-4 rounded hover:text-[#ffc107]">Checkout</button>
    </form>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import axios from 'axios';
  import { useRouter } from 'vue-router';
  
  import { useCartStore } from '@/store/cart';
  
  const useDefaultAddress = ref(false);
  const isDifferentAddress = ref(false);
  const router = useRouter();
  const cartStore = useCartStore();
  
  const billing = ref({
    firstName: '',
    lastName: '',
    companyName: '',
    country: '',
    streetAddress: '',
    apartment: '',  
    city: '',
    state: '',
    phone: '',
    email: '',
  });
  
  const shipping = ref({
    firstName: '',
    lastName: '',
    companyName: '',
    country: '',
    streetAddress: '',
    apartment: '',
    city: '',
    state: '',
    phone: '',
    email: '',
  });
  
  const paymentMethod = ref('');
  
  const submitForm = async () => {
    try {
      // Construct the payload
      const payload = {
        useDefaultAddress: useDefaultAddress.value,
        billing: useDefaultAddress.value ? null : billing.value,
        shipping: isDifferentAddress.value ? shipping.value : null,
        paymentMethod: paymentMethod.value,
      };
  
      // Log the payload for debugging (optional)
      console.log("Final Payload:", payload);
      
  
      // Send the payload to the server with credentials
      const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/create-checkout-session/`, payload, {
        withCredentials: true,
      });
  
      // Redirect to payment page (Stripe or PayPal)
      if (paymentMethod.value === 'stripe') {
        window.location.href = response.data.url;
      } else if (paymentMethod.value === 'paypal') {
        window.location.href = response.data.paypalUrl;
      }
      
     
  
      // Handle the successful response
      console.log('Checkout successful:', response.data);
    } catch (error) {
      // Handle errors
      console.error('Checkout error:', error.response?.data || error.message);
    }
  };
  </script>
  
  <style scoped></style>
  