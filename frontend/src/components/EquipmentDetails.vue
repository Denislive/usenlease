<template>
  <div v-if="loading" class="loading">Loading equipment details...</div>
  <div v-else-if="error" class="error">{{ error }}</div>
  <div v-else-if="equipment" class="cell medium-4 large-4 p-12 border rounded-lg shadow-lg bg-gray-100">
    <h1 class="product-name text-2xl font-bold mb-2">{{ equipment.name }}</h1>

    <div class="rating-reviews mb-2">
      <span class="rating text-yellow-500">{{ renderStars(equipment.rating) }}</span>
      <span class="reviews text-gray-600"> ({{ equipment.equipment_reviews ? equipment.equipment_reviews.length : 0 }}
        Reviews)</span>
    </div>

    <p class="price text-xl font-semibold mb-4">${{ equipment.hourly_rate }}/Hour</p>

    <p class="description mb-4">{{ equipment.description }}</p>
    <p class="availability mb-2">
      <strong>Status:</strong>
      <span :class="equipment.is_available ? 'text-green-600' : 'text-red-600'">
        {{ equipment.is_available ? 'Available' : 'Not Available' }}
      </span>
    </p>

    <div class="address mb-4">
      <h2 class="text-lg font-semibold">Location:</h2>
      <p>{{ equipment.address?.street_address }}</p>
      <p v-if="equipment.address?.street_address2">{{ equipment.address.street_address2 }}</p>
      <p>{{ equipment.address?.city }}, {{ equipment.address?.state }} {{ equipment.address?.zip_code }}</p>
      <p>{{ equipment.address?.country }}</p>
    </div>

    <div class="booking-form">
      <form @submit.prevent="submitBooking">
        <label for="start-date" class="block mb-1">Start Date:</label>
        <input type="date" id="start-date" v-model="startDate" required class="mb-4 p-2 border rounded w-full" />

        <label for="end-date" class="block mb-1">End Date:</label>
        <input type="date" id="end-date" v-model="endDate" required class="mb-4 p-2 border rounded w-full" />

        <label for="quantity" class="block mb-1">Number of Equipments:</label>
        <input type="number" id="quantity" v-model="quantity" min="1" required class="mb-4 p-2 border rounded w-full" />

        <button type="submit"
          class="button add-to-cart bg-[#ffc107] text-black py-2 px-4 rounded hover:bg-yellow-400 transition">
          Add to Cart
        </button>

        <!-- Trigger Chat Creation and Navigation -->
        <RouterLink v-if="authStore.isAuthenticated && props.equipment.owner !== authStore.user.id"
          :to="{ path: '/profile', query: { section: 'chats' } }" @click="createChat"
          class="text-black py-2 px-4 rounded">
          Talk to Owner
        </RouterLink>


      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth'; // Correct import
import { useCartStore } from '@/store/cart'; // Adjust the path as necessary
import useNotifications from '@/store/notification';
import axios from 'axios';  // Import axios
import { useChatStore } from '@/store/chat';

const authStore = useAuthStore(); // Initialize the auth store
const chatStore = useChatStore();

const api_base_url = import.meta.env.VITE_API_BASE_URL;

const props = defineProps({
  equipment: {
    type: Object,
    default: () => ({}), // Provide a default empty object
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
});

const cartStore = useCartStore();
const { showNotification } = useNotifications();

const startDate = ref('');
const endDate = ref('');
const quantity = ref(1);

const createChat = async () => {
  const recepient = props.equipment.owner; // Owner's ID
  const chat = await chatStore.createChat(recepient);
};


const submitBooking = async () => {
  // Prepare the payload for booking
  const payload = {
    item: props.equipment.id,
    quantity: quantity.value,
    start_date: startDate.value,
    end_date: endDate.value,
  };

  // Validate start_date: it should not be in the past
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (new Date(payload.start_date) < today) {
    showNotification('Invalid Start Date', 'Start date cannot be in the past.', 'error');
    return;
  }

  // Validate date range
  if (new Date(payload.start_date) > new Date(payload.end_date)) {
    showNotification('Invalid Date Range', 'End date must be after start date.', 'error');
    return;
  }

  // Validate quantity
  if (payload.quantity <= 0) {
    showNotification('Invalid Quantity', 'Quantity must be greater than zero.', 'error');
    return;
  }

  // Check the available quantity for the equipment
  const availableQuantity = props.equipment.available_quantity;
  if (payload.quantity > availableQuantity) {
    showNotification('Insufficient Stock', `Only ${availableQuantity} items available.`, 'error');
    return;
  }

  // If user is authenticated, proceed with backend API
  if (authStore.isAuthenticated) {
    try {
      const response = await axios.post(`${api_base_url}/api/cart-items/`, payload, {
        withCredentials: true, // Ensures cookies are sent with the request
      });
      cartStore.loadCart(); // Refresh the cart after successful addition
      showNotification('Add to Cart', 'Item added to cart!', 'success');
    } catch (error) {
      showNotification('Failed adding to Cart', `Error: ${error.response.data.detail || 'Unknown error'}. Switch to lesee`, 'error');
    }
  } else {
    // Handle for anonymous users using localStorage
    const localPayload = {
      item: props.equipment,
      quantity: quantity.value,
      start_date: startDate.value,
      end_date: endDate.value,
    };

    const existingCart = localStorage.getItem("cart");
    if (existingCart) {
      const parsedExistingCart = JSON.parse(existingCart);
      if (Array.isArray(parsedExistingCart)) {
        const existingItemIndex = parsedExistingCart.findIndex(
          (cartItem) =>
            cartItem.item.id === localPayload.item.id &&
            cartItem.start_date === localPayload.start_date &&
            cartItem.end_date === localPayload.end_date
        );

        if (existingItemIndex !== -1) {
          // Check if the total quantity exceeds the available stock
          const newQuantity = parsedExistingCart[existingItemIndex].quantity + localPayload.quantity;

          if (newQuantity > availableQuantity) {
            showNotification(
              "Quantity Error",
              `Adding this quantity exceeds the available stock. Only ${availableQuantity} items are available.`,
              "error"
            );
            return; // Prevent adding to the cart if it exceeds availability
          }

          parsedExistingCart[existingItemIndex].quantity = newQuantity;
        } else {
          parsedExistingCart.push(localPayload);
        }

        cartStore.cart = parsedExistingCart;
        localStorage.setItem("cart", JSON.stringify(parsedExistingCart));
      }
    } else {
      const newCart = [localPayload];
      localStorage.setItem("cart", JSON.stringify(newCart));
      cartStore.cart = newCart;
    }

    showNotification("Add to Cart", `Item added to the cart!`, "success");
  }
};


const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  const emptyStars = 5 - fullStars - halfStar;

  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(emptyStars);
};
</script>
