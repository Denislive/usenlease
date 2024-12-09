<template>
  <div v-if="loading" class="loading">Loading equipment details...</div>
  <div v-else-if="error" class="error">{{ error }}</div>
  <div v-else-if="equipment" class="cell medium-4 large-4 p-12 border rounded-lg shadow-lg bg-gray-100">
    <h1 class="product-name text-2xl font-bold mb-2">{{ equipment.name }}</h1>

    <div class="rating-reviews mb-2">
      <span class="rating text-yellow-500">{{ renderStars(equipment.rating) }}</span>
      <span class="reviews text-gray-600"> ({{ equipment.equipment_reviews ? equipment.equipment_reviews.length : 0 }} Reviews)</span>
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
        <RouterLink
          :to="{ path: '/profile', query: {section: 'chats'} }"
          @click="createChat"
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

const authStore = useAuthStore(); // Initialize the auth store

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
  if (authStore.isAuthenticated) {
    const receiver = props.equipment.owner;

    try {
      const response = await axios.post(`${api_base_url}/api/accounts/chats/`, 
        {
          participants: [props.equipment.owner] // Including both sender and receiver in the participants array
        },
        {
          withCredentials: true,  // Ensures cookies are sent with the request
        }
      );
      showNotification('Chat Created', `Successfully started a chat with the owner!`, 'success');
    } catch (error) {
      showNotification('Chat Error', `Error starting chat with the owner!`, 'error');
    }
  } else {
    showNotification('Authentication Required', `Please log in to start a chat!`, 'error');
  }
};



const submitBooking = async () => {
  // Prepare the payload for booking
  const payload = {
    item: props.equipment.id,
    quantity: quantity.value,
    start_date: startDate.value,
    end_date: endDate.value,
  };

  if (authStore.isAuthenticated) {
    try {
      const response = await axios.post(`${api_base_url}/api/cart-items/`, payload, {
        withCredentials: true,  // Ensures cookies are sent with the request
      });
      cartStore.loadCart();
      showNotification('Add to Cart', `Added to cart!`, 'success');
    } catch (error) {
      showNotification('Add to cart', 'Error adding to cart!', 'error');
    }
  } else {
    const localPayload = {
      item: props.equipment,
      quantity: quantity.value,
      start_date: startDate.value,
      end_date: endDate.value,
    };

    const existingCart = localStorage.getItem('cart');
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
          parsedExistingCart[existingItemIndex].quantity += localPayload.quantity;
        } else {
          parsedExistingCart.push(localPayload);
        }

        cartStore.cart = parsedExistingCart;
        localStorage.setItem('cart', JSON.stringify(parsedExistingCart));
      }
    } else {
      const newCart = [localPayload];
      localStorage.setItem('cart', JSON.stringify(newCart));
      cartStore.cart = newCart;
    }
  }
};

const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  const emptyStars = 5 - fullStars - halfStar;

  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(emptyStars);
};
</script>
