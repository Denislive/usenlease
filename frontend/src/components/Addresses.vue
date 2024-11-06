<template>
      <!-- Checkout page section -->
         <form @submit.prevent="submitForm">
            <h3 class="text-2xl font-semibold text-gray-800 mb-4">Billing Details</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
  
              <div>
                <label class="block text-gray-700">First Name <span class="text-red-500">*</span></label>
                <input v-model="billing.firstName" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>
              <div>
                <label class="block text-gray-700">Last Name <span class="text-red-500">*</span></label>
                <input v-model="billing.lastName" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>
              
              <div>
                <label class="block text-gray-700">Company Name</label>
                <input v-model="billing.companyName" type="text" class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>
              
              <div>
                <label class="block text-gray-700" for="country">Country <span class="text-red-500">*</span></label>
                <select v-model="billing.country" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]">
                  <option value="">Select Country</option>
                  <option value="USA">USA</option>
                </select>
              </div>
  
              <div>
                <label class="block text-gray-700">Street Address <span class="text-red-500">*</span></label>
                <input v-model="billing.streetAddress" placeholder="House number and street name" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>
  
              <div>
                <input v-model="billing.apartment" placeholder="Apartment, suite, unit etc. (optional)" type="text" class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>
  
              <div>
                <label class="block text-gray-700">Town / City <span class="text-red-500">*</span></label>
                <input v-model="billing.city" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>
  
              <div>
                <label class="block text-gray-700">State / County <span class="text-red-500">*</span></label>
                <input v-model="billing.state" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>
  
              <div>
                <label class="block text-gray-700">Phone <span class="text-red-500">*</span></label>
                <input v-model="billing.phone" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>
              
              <div>
                <label class="block text-gray-700">Email Address <span class="text-red-500">*</span></label>
                <input v-model="billing.email" type="email" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>
  
              <div class="col-span-2">
                <div class="flex items-center">
                  <input id="address" type="checkbox" v-model="isDifferentAddress" class="mr-2">
                  <label for="address" class="text-gray-700">Ship to a different address?</label>
                </div>
              </div>
  
              <div v-if="isDifferentAddress" class="col-span-2 mt-4">
                <h4 class="text-lg font-semibold text-gray-800 mb-2">Shipping Address</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-gray-700">First Name <span class="text-red-500">*</span></label>
                    <input v-model="shipping.firstName" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
                  </div>
                  <div>
                    <label class="block text-gray-700">Last Name <span class="text-red-500">*</span></label>
                    <input v-model="shipping.lastName" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
                  </div>
                  
                  <div>
                    <label class="block text-gray-700">Company Name</label>
                    <input v-model="shipping.companyName" type="text" class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
                  </div>
                  
                  <div>
                    <label class="block text-gray-700" for="country_name">Country <span class="text-red-500">*</span></label>
                    <select v-model="shipping.country" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]">
                      <option value="">Select Country</option>
                      <option value="Bangladesh">Bangladesh</option>
                      <option value="Algeria">Algeria</option>
                      <option value="Afghanistan">Afghanistan</option>
                      <option value="Ghana">Ghana</option>
                      <option value="Albania">Albania</option>
                      <option value="Bahrain">Bahrain</option>
                      <option value="Colombia">Colombia</option>
                      <option value="Dominican Republic">Dominican Republic</option>
                    </select>
                  </div>
  
                  <div>
                    <label class="block text-gray-700">Street Address <span class="text-red-500">*</span></label>
                    <input v-model="shipping.streetAddress" placeholder="House number and street name" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
                  </div>
  
                  <div>
                    <input v-model="shipping.apartment" placeholder="Apartment, suite, unit etc. (optional)" type="text" class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
                  </div>
  
                  <div>
                    <label class="block text-gray-700">Town / City <span class="text-red-500">*</span></label>
                    <input v-model="shipping.city" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
                  </div>
  
                  <div>
                    <label class="block text-gray-700">State / County <span class="text-red-500">*</span></label>
                    <input v-model="shipping.state" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
                  </div>
  
                  <div>
                    <label class="block text-gray-700">Phone <span class="text-red-500">*</span></label>
                    <input v-model="shipping.phone" type="text" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
                  </div>
                  
                  <div>
                    <label class="block text-gray-700">Email Address <span class="text-red-500">*</span></label>
                    <input v-model="shipping.email" type="email" required class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
                  </div>
                </div>
              </div>
  
              <div class="col-span2">
                <label for="order_note" class="block text-gray-700">Order Notes</label>
                <textarea v-model="orderNote" cols="70" rows="8" id="order_note" placeholder="Notes about your order, e.g. special notes for delivery." class="mt-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-[#1c1c1c]"></textarea>
              </div>
            </div>
            <button type="submit" class="mt-4 bg-[#1c1c1c] text-white py-2 px-4 rounded hover:text-[#ffc107]">checkoout</button>
          </form>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const isDifferentAddress = ref(false);
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
      const orderNote = ref('');
  
      const submitForm = () => {
        console.log("Billing Information:", billing.value);
        if (isDifferentAddress.value) {
          console.log("Shipping Information:", shipping.value);
        }
        console.log("Order Note:", orderNote.value);
        // Add logic to handle form submission (e.g., API call)
      };

  </script>
  
  <style scoped>
  </style>