
<template>
    <div class="container md:py-1 lg:py-1 mx-auto sm:p-0">
      <!-- Shopping Cart Area Start -->
      <div class="mt-0">
        <form @submit.prevent="submitCart">
          <h3 class="bg-gray-800 text-white p-4 mb-4">Cart Summary</h3>
          <div class="overflow-x-auto p-2">
            <table class="min-w-full bg-white border border-gray-300">
              <thead>
                <tr>
                  <th class="py-2 px-4 border-b text-left">Delete</th>
                  <th class="py-2 px-4 border-b text-left">Image</th>
                  <th class="py-2 px-4 border-b text-left">Product</th>
                  <th class="py-2 px-4 border-b text-left">Price</th>
                  <th class="py-2 px-4 border-b text-left">Quantity</th>
                  <th class="py-2 px-4 border-b text-left">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in cartItems" :key="item.id">
                  <td class="py-2 px-4 border-b">
                    <button @click.prevent="removeFromCart(item)">
                      <i class="pi pi-trash text-red-500"></i>
                    </button>
                  </td>
                  <td class="py-2 px-4 border-b">
                    <img :src="`http://127.0.0.1:8000${getItemImage(item)}`" alt="" class="w-20 h-20 object-cover" />
                  </td>
                  <td class="py-2 px-4 border-b">
                    <a href="#" class="text-blue-600 hover:underline">{{ getItemName(item) }}</a>
                  </td>
                  <td class="py-2 px-4 border-b">${{ getItemPrice(item) }}</td>
                  <td class="py-2 px-4 border-b">
                    <div class="border-b">
                      <button @click.prevent="adjustQuantity(item, -1)" class="text-red-500 m-0"
                        :disabled="item.quantity <= 1">
                        <i class="pi pi-minus lg:mr-4"></i>
                      </button>
                      <span class="mx-2 text-xl">{{ item.quantity }}</span>
                      <button @click.prevent="adjustQuantity(item, 1)" class="text-yellow-500">
                        <i class="pi pi-plus lg:ml-4"></i>
                      </button>
                    </div>
                  </td>
                  <td class="py-2 px-4 border-b">${{ calculateItemTotal(item) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
  
          <!-- Cart Totals Area Start -->
          <div class="mt-8">
            <h3 class="font-semibold bg-gray-800 text-white p-4 mb-4">Cart Totals</h3>
            <div class="m-4">
              <div class="flex justify-between">
                <p>Subtotal</p>
                <p class="font-semibold">${{ subtotal }}</p>
              </div>
              <div class="flex justify-between">
                <p>Shipping</p>
                <p class="font-semibold">Flat Rate: $25.00</p>
              </div>
              <div class="flex justify-between mt-2">
                <p>Total</p>
                <p class="font-semibold">${{ (subtotal + 25).toFixed(2) }}</p>
              </div>
            </div>
            <div class="text-right m-4">
              <button @click.prevent="checkout"
                class="bg-[#1c1c1c] text-white py-2 px-4 rounded hover:text-[#ffc107] transition">Proceed to
                Checkout</button>
            </div>
          </div>
          <!-- Cart Totals Area End -->
        </form>
      </div>
      <!-- Shopping Cart Area End -->
    </div>
  </template>
  
  <script>
  import { computed, onMounted } from 'vue';
  import { useCartStore } from '@/store/cart';
  import { useAuthStore } from '@/store/auth';
  import axios from 'axios';
  
  export default {
    setup() {
      const cartStore = useCartStore();
      const authStore = useAuthStore();
  
      onMounted(() => {
        cartStore.loadCart();
      });
  
      const removeFromCart = async (item) => {
        if (authStore.isAuthenticated) {
          cartStore.removeItem(item.id);
          try {
            await axios.delete(`${import.meta.env.VITE_API_BASE_URL}/api/cart-items/${item.id}/`, {
              withCredentials: true,
            });
          } catch (error) {
            console.error("Error deleting item:", error);
          }
        } else {
          cartStore.removeItem(item.id);
        }
      };
  
      const calculateItemTotal = (item) => {
        return authStore.isAuthenticated ? item.item_details.hourly_rate * item.quantity: item.item.hourly_rate * item.quantity;
      };
  
      const adjustQuantity = async (item, adjustment) => {
        const newQuantity = item.quantity + adjustment;
        if (newQuantity > 0) {
          cartStore.updateItemQuantity(item.id, newQuantity);
  
          if (authStore.isAuthenticated) {
            const payload = {
              id: item.id,
              quantity: newQuantity,
              start_date: item.item_details.start_date,
              end_date: item.item_details.end_date,
              total: item.item_details.hourly_rate * newQuantity,
            };
  
            try {
              await axios.put(`${import.meta.env.VITE_API_BASE_URL}/api/cart-items/${payload.id}/`, payload, {
                withCredentials: true,  // Ensures cookies are sent with the request
              });
              console.log("Cart item updated in the database");
            } catch (error) {
              console.error("Error updating cart item:", error);
            }
          } else {
            // Save to localStorage for anonymous users
            const cartFromStorage = JSON.parse(localStorage.getItem('cart')) || [];
            console.log("CArt form local storage", cartFromStorage)
            const existingItemIndex = cartFromStorage.findIndex(i => i.id === item.id);
  
            if (existingItemIndex !== -1) {
              cartFromStorage[existingItemIndex].quantity = newQuantity;
              cartFromStorage[existingItemIndex].total = item.item.hourly_rate * newQuantity;
              cartStore.updateItemQuantity(item.item.id, newQuantity);
            localStorage.setItem('cart', JSON.stringify(cartFromStorage));
            console.log("FoundCart updated in local storage for anonymous user");
  
            } else {
              cartFromStorage.push({ ...item, quantity: newQuantity });
              localStorage.setItem('cart', JSON.stringify(cartFromStorage));
            console.log("Cart updated in local storage for anonymous user");
  
            }
          }
        }
      };
  
  
      const subtotal = computed(() => {
        return authStore.isAuthenticated ? cartStore.cart.reduce((total, item) => total + item.item_details.hourly_rate * item.quantity, 0) : cartStore.cart.reduce((total, item) => total + item.item.hourly_rate * item.quantity, 0);
  
      });
  
  
      const getItemImage = (item) => {
        return authStore.isAuthenticated ? item.item_details.images[0].image_url : item.item.images[0].image_url;
      };
  
      const getItemName = (item) => {
        return authStore.isAuthenticated ? item.item_details.name : item.item.name;
      };
  
      const getItemPrice = (item) => {
        return authStore.isAuthenticated ? item.item_details.hourly_rate : item.item.hourly_rate;
      };
  
  
      return {
        cartItems: computed(() => cartStore.cart),
        subtotal,
        removeFromCart,
        adjustQuantity,
        calculateItemTotal,
        getItemImage,
        getItemName,
        getItemPrice,
      };
    },
  };
  </script>
  
  <style scoped>
  /* Add any additional styles here */
  </style>
  