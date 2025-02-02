<template>
  <div v-if="loading" class="loading">Loading equipment details...</div>
  <div v-else-if="error" class="error">{{ error }}</div>
  <div v-else-if="equipment && Object.keys(equipment).length" class="cell medium-4 large-4 p-12 border rounded-lg shadow-lg bg-gray-100">
    

     <!-- Additional notification about partial availability -->
     <div v-if="partialAvailabilityMessage" class="availability-notification bg-green-200 text-green-800 p-2 rounded mb-2">
      {{ partialAvailabilityMessage }}
    </div>


    <!-- Notification about availability dates -->
    <div v-if="!equipment.is_available" class="availability-notification bg-blue-200 text-blue-800 p-2 rounded mb-2">
      Available after: {{ nextAvailableDate }}
    </div>

   

    <h1 class="product-name text-2xl font-bold mb-2">{{ equipment.name }}</h1>

    <div class="rating-reviews mb-2">
      <span class="rating text-yellow-500">{{ renderStars(equipment.rating) }}</span>
      <span class="reviews text-gray-600"> ({{ equipment.equipment_reviews ? equipment.equipment_reviews.length : 0 }} Reviews)</span>
    </div>

    <p class="price text-xl font-semibold mb-4">${{ equipment.hourly_rate }}/Day</p>

    <p class="description mb-4">{{ equipment.description }}</p>
    <p class="availability mb-2">
      <strong>Status:</strong>
      <span :class="equipment.is_available ? 'text-green-600' : 'text-red-600'">
        {{ equipment.is_available ? `${equipment.available_quantity } Available` : `Booked until ${nextAvailableDate}` }}
      </span>
    </p>

    <div class="address mb-4">
      <h2 class="text-lg font-semibold">Location:</h2>
      <p>{{ equipment.address?.street_address }}</p>
      <p v-if="equipment.address?.street_address2">{{ equipment.address.street_address2 }}</p>
      <p>{{ equipment.address?.city }}, {{ equipment.address?.state }} {{ equipment.address?.zip_code }}</p>
      <p>{{ equipment.address?.country }}</p>

      <div class="mt-2">
        <h3 class="text-md font-semibold">Tags:</h3>
        <div class="flex flex-wrap gap-2">
          <span v-for="tag in equipment.tags" :key="tag.name" class="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium">
            {{ tag.name }}
          </span>
        </div>
      </div>
    </div>

    <div class="booking-form">
      <form @submit.prevent="submitBooking">
        <label for="start-date" class="block mb-1">Start Date:</label>
        <input type="date" id="start-date" v-model="startDate" :min="today" :disabled="isFullyBooked" required class="mb-4 p-2 border rounded w-full" :class="{ 'disabled-date': isDateBooked(startDate), 'partially-booked-date': isPartiallyBooked(startDate) }" />
        <p v-if="dateError" class="error-message">{{ dateError }}</p>

        <label for="end-date" class="block mb-1">End Date:</label>
        <input type="date" id="end-date" v-model="endDate" :min="startDate" :disabled="isFullyBooked" required class="mb-4 p-2 border rounded w-full" :class="{ 'disabled-date': isDateBooked(endDate), 'partially-booked-date': isPartiallyBooked(endDate) }" />
        <p v-if="dateError" class="error-message">{{ dateError }}</p>

        <label for="quantity" class="block mb-1">Number of Equipments:</label>
        <input type="number" id="quantity" v-model="quantity" min="1" :max="equipment.available_quantity" @input="validateQuantity" required class="mb-4 p-2 border rounded w-full" />
        <p v-if="quantityError" class="error-message">{{ quantityError }}</p>

        <button type="submit" class="button add-to-cart bg-[#ffc107] text-black py-2 px-4 rounded hover:bg-yellow-400 transition" :disabled="isFullyBooked">
          Add to Cart
        </button>

        <RouterLink v-if="authStore.isAuthenticated && props.equipment.owner !== authStore.user.id" :to="{ path: '/profile', query: { section: 'chats' } }" @click="createChat" class="text-black py-2 px-4 rounded">
          Talk to Owner
        </RouterLink>
      </form>
    </div>
  </div>
</template>

<script setup>
// filepath: /home/techbro/Desktop/usenlease/frontend/src/components/EquipmentDetails.vue
import { ref, computed } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useCartStore } from '@/store/cart';
import useNotifications from '@/store/notification';
import axios from 'axios';
import { useChatStore } from '@/store/chat';

const authStore = useAuthStore();
const chatStore = useChatStore();

const api_base_url = import.meta.env.VITE_API_BASE_URL;

const props = defineProps({
  equipment: {
    type: Object,
    default: () => ({}),
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
const dateError = ref('');
const quantityError = ref('');

const today = new Date().toISOString().split('T')[0];

const isFullyBooked = computed(() => props.equipment.available_quantity === 0);

const createChat = async () => {
  const recepient = props.equipment.owner;
  const chat = await chatStore.createChat(recepient, props.equipment);
};

const isDateRangePartiallyBooked = (start, end, quantity) => {
  let totalBooked = 0;

  for (let i = 0; i < props.equipment.booked_dates.length; i++) {
    const bookedStart = new Date(props.equipment.booked_dates[i].start_date);
    const bookedEnd = new Date(props.equipment.booked_dates[i].end_date);
    const rangeStart = new Date(start);
    const rangeEnd = new Date(end);

    // Check if the selected range overlaps with the booked range
    if (
      (rangeStart >= bookedStart && rangeStart <= bookedEnd) ||
      (rangeEnd >= bookedStart && rangeEnd <= bookedEnd) ||
      (rangeStart <= bookedStart && rangeEnd >= bookedEnd)
    ) {
      totalBooked++;
    }
  }

  // Check if the remaining quantity after booking is sufficient
  return totalBooked + quantity > props.equipment.available_quantity;
};

const validateQuantity = () => {
  quantityError.value = '';

  if (quantity.value <= 0) {
    quantityError.value = 'Quantity must be greater than zero.';
  } else if (quantity.value > props.equipment.available_quantity) {
    quantityError.value = `Only ${props.equipment.available_quantity} items available.`;
  }
};

const submitBooking = async () => {
  dateError.value = '';
  quantityError.value = '';

  validateQuantity();
  if (quantityError.value) {
    return;
  }

  const payload = {
    item: props.equipment.id,
    quantity: quantity.value,
    start_date: startDate.value,
    end_date: endDate.value,
  };

  // Check if selected dates are fully booked
  if (isDateRangePartiallyBooked(startDate.value, endDate.value, quantity.value)) {
    showNotification('Unavailable Item', `The selected dates are currently booked. Please choose different dates.`, 'error');
    return;
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (new Date(payload.start_date) < today) {
    dateError.value = 'Start date cannot be in the past.';
    return;
  }

  if (new Date(payload.start_date) > new Date(payload.end_date)) {
    dateError.value = 'End date must be after start date.';
    return;
  }

  if (payload.quantity <= 0) {
    quantityError.value = 'Quantity must be greater than zero.';
    return;
  }

  const availableQuantity = props.equipment.available_quantity;
  if (payload.quantity > availableQuantity) {
    quantityError.value = `Only ${availableQuantity} items available.`;
    return;
  }

  if (authStore.isAuthenticated) {
    try {
      const response = await axios.post(`${api_base_url}/api/cart-items/`, payload, {
        withCredentials: true,
      });
      cartStore.loadCart();
      showNotification('Add to Cart', 'Item added to cart!', 'success');
    } catch (error) {
      showNotification('Failed adding to Cart', `Error: ${error.response.data.error || error.response.data.detail || 'Unknown error'}`, 'error');
    }
  } else {
    const plainEquipment = JSON.parse(JSON.stringify(props.equipment));

    const localPayload = {
      item: plainEquipment,
      quantity: quantity.value,
      start_date: startDate.value,
      end_date: endDate.value,
    };

    try {
      const existingCart = await cartStore.getIndexedDBData();

      const existingItemIndex = existingCart.findIndex((cartItem) => cartItem.item.id === localPayload.item.id);

      if (existingItemIndex !== -1) {
        const newQuantity = existingCart[existingItemIndex].quantity + localPayload.quantity;

        if (newQuantity > availableQuantity) {
          quantityError.value = `Adding this quantity exceeds available stock. Only ${availableQuantity} items are available.`;
          return;
        }

        existingCart[existingItemIndex].quantity = newQuantity;
        showNotification('Updated Quantity', 'Quantity updated in the cart!', 'info');
      } else {
        existingCart.push(localPayload);
        showNotification('Add to Cart', 'Item added to the cart!', 'success');
      }

      await cartStore.saveIndexedDBData(existingCart);
      cartStore.cart = existingCart;
    } catch (error) {
      showNotification('Error', 'Failed to update cart in IndexedDB.', 'error');
      console.error('IndexedDB Error:', error);
    }
  }
};

const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  const emptyStars = 5 - fullStars - halfStar;

  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(emptyStars);
};

const isDateBooked = (date) => {
  return props.equipment.booked_dates.some((range) => {
    const start = new Date(range.start_date);
    const end = new Date(range.end_date);
    const checkDate = new Date(date);
    return checkDate >= start && checkDate <= end;
  });
};

const isPartiallyBooked = (date) => {
  return props.equipment.booked_dates.some((range) => {
    const start = new Date(range.start_date);
    const end = new Date(range.end_date);
    const checkDate = new Date(date);
    return checkDate >= start && checkDate <= end && props.equipment.available_quantity > 1;
  });
};

const bookedDates = computed(() => {
  return props.equipment.booked_dates.map(range => `${range.start_date} to ${range.end_date}`).join(', ');
});

const nextAvailableDate = computed(() => {
  const lastBookedDate = props.equipment.booked_dates.reduce((latest, range) => {
    const endDate = new Date(range.end_date);
    return endDate > latest ? endDate : latest;
  }, new Date(0));

  return new Date(lastBookedDate.setDate(lastBookedDate.getDate() + 1)).toISOString().split('T')[0];
});

const partialAvailabilityMessage = computed(() => {
  const now = new Date();
  const availablePeriods = [];

  for (let i = 0; i < props.equipment.booked_dates.length - 1; i++) {
    const currentEnd = new Date(props.equipment.booked_dates[i].end_date);
    const nextStart = new Date(props.equipment.booked_dates[i + 1].start_date);

    if (currentEnd < nextStart) {
      const diffDays = Math.ceil((nextStart - currentEnd) / (1000 * 60 * 60 * 24));
      if (diffDays >= 1) {
        availablePeriods.push(`${currentEnd.toISOString().split('T')[0]} to ${nextStart.toISOString().split('T')[0]}`);
      }
    }
  }

  return availablePeriods.length > 0 ? `Available for rent on: ${availablePeriods.join(', ')}` : '';
});
</script>

<style>
.disabled-date {
  pointer-events: none;
  opacity: 0.6;
}

.partially-booked-date {
  opacity: 0.6;
}

.error-message {
  color: red;
  font-size: 0.875rem;
  margin-top: -0.5rem;
  margin-bottom: 1rem;
}
</style>