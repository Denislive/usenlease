<template>
  <div class="container md:py-1 lg:py-1 mx-auto sm:p-0">
    <!-- Shopping Cart Area Start -->
    <div class="mt-0">
      <form @submit.prevent="submitCart">
        <h3 class="bg-gray-800 text-white p-4 mb-4">Cart Summary</h3>

        <!-- Cart Items Table -->
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
                  <img :src="`${getItemImage(item)}`" alt="" class="w-20 h-20 object-cover" />
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

        <!-- Empty Cart Message -->
        <div v-if="cartItems.length === 0" class="empty-cart text-center py-16">
          <i class="pi pi-exclamation-circle text-9xl text-gray-500"></i>

          <p class="text-xl text-gray-500 mt-4">Oops! Your cart is empty.</p>
          <p class="text-sm text-gray-400 mt-2">Add some items to your cart to get started!</p>
        </div>

        <!-- Cart Totals Area Start -->
        <div class="mt-8" v-if="cartItems.length > 0">
          <h3 class="font-semibold bg-gray-800 text-white p-4 mb-4">Cart Totals</h3>
          <div class="m-4">
            <div class="flex justify-between">
              <p>Subtotal</p>
              <p class="font-semibold">${{ subtotal }}</p>
            </div>
            <div class="flex justify-between">
              <p>Shipping</p>
              <p class="font-semibold">Flat Rate: $0.00</p>
            </div>
            <div class="flex justify-between mt-2">
              <p>Total</p>
              <p class="font-semibold">${{ (subtotal + 0).toFixed(2) }}</p>
            </div>
          </div>
          <div class="text-right m-4">
            <RouterLink :to="{ name: 'checkout' }"
              class="bg-[#1c1c1c] text-white py-2 px-4 rounded hover:text-[#ffc107] transition">Proceed to
              Checkout</RouterLink>
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
import useNotifications from '@/store/notification.js'; // Import the notification service
const { showNotification } = useNotifications(); // Initialize notification service


export default {
  setup() {
    const cartStore = useCartStore();
    const authStore = useAuthStore();

    const api_base_url = import.meta.env.VITE_API_BASE_URL;


    // Load cart data when the component is mounted
    onMounted(async () => {

      cartStore.loadCart();
    });


    const removeFromCart = async (item) => {
      if (authStore.isAuthenticated) {
        cartStore.removeItem(item.id);
        try {
          await axios.delete(`${api_base_url}/api/cart-items/${item.id}/`, {
            withCredentials: true,
          });
          showNotification('Item Removed', `${item.item_details.name} has been removed from your cart.`, 'success'); // Show success notification

        } catch (error) {
          showNotification('Error', `Error deleting ${item.name}.`, 'error'); // Show error notification

        }
      } else {
        cartStore.removeItem(item.id);
      }
    };


    const adjustQuantity = async (item, adjustment) => {
      const newQuantity = item.quantity + adjustment;
      if (newQuantity > 0) {

        if (authStore.isAuthenticated) {
          const payload = {
            id: item.id,
            quantity: newQuantity,
            start_date: item.item_details.start_date,
            end_date: item.item_details.end_date,
            total: item.item_details.hourly_rate * newQuantity,
          };

          try {
            const response = await axios.put(`${api_base_url}/api/cart-items/${payload.id}/`, payload, {
              withCredentials: true,  // Ensures cookies are sent with the request
            });
            cartStore.updateItemQuantity(item.id, newQuantity);

          } catch (error) {
            showNotification('Error', `You can not add more than ${item.quantity} of ${item.item_details.name} to cart!`, 'error'); // Show error notification
          }
        } else {
          // Save to localStorage for anonymous users
          // Loop through each item in the cart and log its details
          const savedCart = localStorage.getItem('cart');
          if (savedCart) {
            cartStore.cart = JSON.parse(savedCart);
          }

          cartStore.cart.forEach((storedItem, index) => {
            if (storedItem.item.id == item.item.id) {
              cartStore.updateItemQuantity(storedItem.item.id, newQuantity);
            }
          });

        }
      }
    };


    const calculateItemTotal = (item) => {
      const price = authStore.isAuthenticated && item.item_details
        ? item.item_details.hourly_rate
        : item.item
          ? item.item.hourly_rate
          : 0; // Fallback price if neither item_details nor item exists

      return price * item.quantity;
    };

    const subtotal = computed(() => {
      return cartStore.cart.reduce((total, item) => {
        const price = authStore.isAuthenticated && item.item_details
          ? item.item_details.hourly_rate
          : item.item
            ? item.item.hourly_rate
            : 0; // Fallback price if neither item_details nor item exists

        // Calculate the time difference between start_date and end_date in hours
        const startDate = new Date(item.start_date);
        const endDate = new Date(item.end_date);
        const timeDiff = endDate - startDate; // Time difference in milliseconds
        const hours = timeDiff / (1000 * 3600); // Convert milliseconds to hours

        // Return the total calculated based on price, quantity, and hours
        return total + price * item.quantity;
      }, 0);
    });



    const getItemImage = (item) => {
      if (authStore.isAuthenticated && item.item_details && item.item_details.images && item.item_details.images.length > 0) {
        return item.item_details.images[0].image_url;
      } else if (item.item && item.item.images && item.item.images.length > 0) {
        return item.item.images[0].image_url;
      } else {
        // Return a placeholder image URL or null to handle it in the template
        return item.item.name || item.item_details.name; // Or return null if you handle the fallback in the template
      }
    };

    const getItemName = (item) => {
      return authStore.isAuthenticated && item.item_details
        ? item.item_details.name
        : item.item
          ? item.item.name
          : 'Unknown'; // Fallback name
    };

    const getItemPrice = (item) => {
      return authStore.isAuthenticated && item.item_details
        ? item.item_details.hourly_rate
        : item.item
          ? item.item.hourly_rate
          : 0; // Fallback price
    };




    return {
      api_base_url,
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