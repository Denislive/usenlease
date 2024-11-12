<template>
  <div v-if="loading" class="loading">Loading equipment details...</div>
  <div v-else-if="error" class="error">{{ error }}</div>
  <div v-else-if="equipment" class="cell medium-4 large-4 p-4 border rounded-lg shadow-lg bg-white">
    <h1 class="product-name text-2xl font-bold mb-2">{{ equipment.name }}</h1>

    <div class="rating-reviews mb-2">
      <span class="rating text-yellow-500">{{ renderStars(equipment.rating) }}</span>
      <span class="reviews text-gray-600"> ({{ equipment.reviews ? equipment.reviews.length : 0 }} Reviews)</span>
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
      </form>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth'; // Correct import
const authStore = useAuthStore(); // Initialize the auth store
import { useCartStore } from '@/store/cart'; // Adjust the path as necessary
const cartStore = useCartStore();
import axios from 'axios';  // Import axios

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

const startDate = ref('');
const endDate = ref('');
const quantity = ref(1);

const submitBooking = async () => {
  console.log('Booking Details:', {
    startDate: startDate.value,
    endDate: endDate.value,
    quantity: quantity.value,
    equipment: props.equipment.id,
  });

  // Prepare the payload
  const payload = {
    item: props.equipment.id,
    quantity: quantity.value,
    start_date: startDate.value,
    end_date: endDate.value,
  };

  if (authStore.isAuthenticated) {
    console.log("Adding equipment to cart", payload);

    try {
      console.log("Synching cart to db ...");
      const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/cart-items/`, payload, {
        withCredentials: true,  // Ensures cookies are sent with the request
      });
      console.log("Item saved to the database:", response.data);
    } catch (error) {
      console.error("Error saving cart:", error);
    }
  } else {
    // Prepare the payload for local storage
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
          // Update the quantity and total for the existing item
          parsedExistingCart[existingItemIndex].quantity += localPayload.quantity;
          parsedExistingCart[existingItemIndex].total =
            parsedExistingCart[existingItemIndex].quantity *
            parsedExistingCart[existingItemIndex].item.hourly_rate;
        } else {
          // Add new item if not already in the cart
          parsedExistingCart.push(localPayload);
        }

        cartStore.cart = parsedExistingCart;
        localStorage.setItem('cart', JSON.stringify(parsedExistingCart));
        console.log("Cart updated with new items, without overwriting.");
      } else {
        // If the existing cart isn't an array, just replace it with the new item
        cartStore.cart = [localPayload];
        localStorage.setItem('cart', JSON.stringify([localPayload]));
        console.log("Cart saved to localStorage.");
      }
    } else {
      // Save the new cart if no existing cart in localStorage
      const newCart = [localPayload];
      localStorage.setItem('cart', JSON.stringify(newCart));
      cartStore.cart = newCart;
      console.log("Cart saved to localStorage.");
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
