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
                <th class="py-2 px-4 border-b text-left">Lease Duration (Days)</th> <!-- New column -->
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
                  <p @click="goToDetail(getItemId(item))" class="text-blue-600 hover:underline">{{ getItemName(item) }}</p>
                </td>
                <td class="py-2 px-4 border-b">${{ getItemPrice(item) }}</td>
                <td class="py-2 px-4 border-b">
                  <div class="flex items-center">
                    <button @click.prevent="adjustQuantity(item, -1)" class="text-red-500 m-0" :disabled="item.quantity <= 1">
                      <i class="pi pi-minus lg:mr-4"></i>
                    </button>
                    <input type="number" v-model.number="item.quantity" @input="debouncedHandleQuantityInput(item)" class="w-16 text-center border rounded" :min="1" :max="item.item_details ? item.item_details.available_quantity : item.item.available_quantity" />
                    <button @click.prevent="adjustQuantity(item, 1)" class="text-yellow-500">
                      <i class="pi pi-plus lg:ml-4"></i>
                    </button>
                  </div>
                </td>

                <!-- Lease Duration Column -->
                <td class="py-2 px-4 border-b">
                  <span>{{ calculateLeaseDuration(item) }} days</span>
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
            <RouterLink :to="{ name: 'checkout' }" class="bg-[#1c1c1c] text-white py-2 px-4 rounded hover:text-[#ffc107] transition">Proceed to Checkout</RouterLink>
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
import { useRouter } from 'vue-router';
const { showNotification } = useNotifications(); // Initialize notification service

function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

export default {
  setup() {
    const cartStore = useCartStore();
    const authStore = useAuthStore();
    const router = useRouter();


    const api_base_url = import.meta.env.VITE_API_BASE_URL;

    // Load cart data when the component is mounted
    onMounted(async () => {
      await cartStore.loadCart(); // Ensure cartStore is loaded asynchronously
      console.log("CART", cartStore.cart);
    });

    const removeFromCart = async (item) => {
      if (authStore.isAuthenticated) {
        cartStore.removeItem(item.id);
        try {
          await axios.delete(`${api_base_url}/api/cart-items/${item.id}/`, {
            withCredentials: true,
          });
          showNotification('Item Removed', `${item.item_details.name} has been removed from your cart.`, 'success');
        } catch (error) {
          showNotification('Error', `Error deleting ${item.name}.`, 'error');
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
            await axios.put(`${api_base_url}/api/cart-items/${payload.id}/`, payload, {
              withCredentials: true,
            });
            cartStore.updateItemQuantity(item.id, newQuantity);
          } catch (error) {
            showNotification('Error', `You can not add more than ${item.quantity} of ${item.item_details.name} to cart!`, 'error');
          }
        } else {
          cartStore.updateItemQuantity(item.id, newQuantity);
        }
      }
    };

    const handleQuantityInput = async (item) => {
      const newQuantity = parseInt(item.quantity);

      // Ensure the quantity is a valid number and within the available quantity range
      if (newQuantity > 0 && newQuantity <= (item.item_details ? item.item_details.available_quantity : item.item.available_quantity)) {
        if (authStore.isAuthenticated) {
          // Update quantity in the cart and API
          const payload = {
            id: item.id,
            quantity: newQuantity,
            start_date: item.item_details ? item.item_details.start_date : item.item.start_date,
            end_date: item.item_details ? item.item_details.end_date : item.item.end_date,
            total: item.item_details ? item.item_details.hourly_rate * newQuantity : item.item.hourly_rate * newQuantity,
          };

          try {
            await axios.put(`${api_base_url}/api/cart-items/${item.id}/`, payload, { withCredentials: true });
            cartStore.updateItemQuantity(item.id, newQuantity);
          } catch (error) {
            showNotification('Error', `Error updating the quantity of ${item.item_details.name}.`, 'error');
          }
        } else {
          cartStore.updateItemQuantity(item.id, newQuantity);
        }
      } else {
        item.quantity = 1;  // Reset to 1 if the value is invalid or exceeds available quantity
        showNotification('Invalid Quantity', `Please enter a valid quantity (max ${item.item_details ? item.item_details.available_quantity : item.item.available_quantity}).`, 'error');
      }
    };
    // Debounce the quantity input handler to prevent multiple API calls
    const debouncedHandleQuantityInput = debounce(handleQuantityInput, 700);

    const calculateItemTotal = (item) => {
      const price = authStore.isAuthenticated && item.item_details
        ? item.item_details.hourly_rate
        : item.item
          ? item.item.hourly_rate
          : 0;
      return price * item.quantity;
    };

    const calculateLeaseDuration = (item) => {
      const startDate = new Date(item.start_date);
      const endDate = new Date(item.end_date);
      const timeDiff = endDate - startDate;
      const days = timeDiff / (1000 * 3600 * 24); // Convert milliseconds to days
      return days;
    };

    const subtotal = computed(() => {
      return cartStore.cart.reduce((total, item) => {
        const price = authStore.isAuthenticated && item.item_details
          ? item.item_details.hourly_rate
          : item.item
            ? item.item.hourly_rate
            : 0;

        const startDate = new Date(item.start_date);
        const endDate = new Date(item.end_date);
        const timeDiff = endDate - startDate;
        const hours = timeDiff / (1000 * 3600);
        return total + price * item.quantity;
      }, 0);
    });

    const getItemImage = (item) => {
      if (authStore.isAuthenticated && item.item_details && item.item_details.images && item.item_details.images.length > 0) {
        return item.item_details.images[0].image_url;
      } else if (item.item && item.item.images && item.item.images.length > 0) {
        return item.item.images[0].image_url;
      } else {
        return item.item.name || item.item_details.name;
      }
    };

    const getItemName = (item) => {
      return authStore.isAuthenticated && item.item_details
        ? item.item_details.name
        : item.item
          ? item.item.name
          : 'Unknown';
    };

    const getItemPrice = (item) => {
      return authStore.isAuthenticated && item.item_details
        ? item.item_details.hourly_rate
        : item.item
          ? item.item.hourly_rate
          : 0;
    };

    const getItemId = (item) => {
      return authStore.isAuthenticated && item.item_details
        ? item.item_details.id
        : item.item
          ? item.item.id
          : 0;
    };

    const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  } else {
    showNotification('Item Error', 'Equipment ID is missing!', 'error');
  }
};

    return {
      api_base_url,
      cartItems: computed(() => cartStore.cart),
      subtotal,
      removeFromCart,
      adjustQuantity,
      calculateItemTotal,
      calculateLeaseDuration,
      getItemId,
      goToDetail,
      getItemImage,
      getItemName,
      getItemPrice,
      debouncedHandleQuantityInput
    };
  },
};
</script>

<style scoped>
/* Add any additional styles here */
</style>