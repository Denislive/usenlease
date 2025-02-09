<template>
  <div v-if="loading" class="loading text-center p-4">Loading equipment details...</div>
  <div v-else-if="error" class="error text-red-500 text-center p-4">{{ error }}</div>
  <div v-else-if="equipment && Object.keys(equipment).length" class="p-6 border rounded-lg shadow-lg bg-white">

    <!-- Product Name -->
    <h1 class="product-name text-3xl font-bold mb-4 border-b pb-2">{{ equipment.name }}</h1>

    <!-- Rating and Reviews -->
    <div class="rating-reviews flex items-center mb-4">
      <span class="rating text-yellow-500 mr-2">{{ renderStars(equipment.rating) }}</span>
      <span class="reviews text-gray-600">({{ equipment.equipment_reviews ? equipment.equipment_reviews.length : 0 }}
        Reviews)</span>
    </div>

    <!-- Price -->
    <p class="price text-2xl font-semibold mb-4">${{ equipment.hourly_rate }}/Day</p>

    <!-- Description -->
    <p class="description mb-4">
      <strong>Description:</strong> {{ equipment.description }}
    </p>

    <!-- Availability Section -->
    <div class="availability-notification bg-gray-100 p-4 rounded-lg border mb-4">
      <h3 class="text-lg font-semibold mb-2">Booking Availability</h3>
      <div v-if="items_data && items_data.length > 0">
        <div v-for="(booking, index) in items_data" :key="index"
          class="booking-item flex items-center justify-between p-2 bg-white shadow-md rounded-md mb-2">
          <p class="text-gray-700">
            <span class="font-semibold">{{ equipment.is_available ? (totalBooked + equipment.available_quantity) -
              booking.quantity : totalBooked - booking.quantity }} Available</span>
            between: <span class="text-blue-600">{{ formatDate(booking.start_date) }}</span>
            - <span class="text-red-500">{{ formatDate(booking.end_date) }}</span>
          </p>
        </div>
        <p class="text-blue-500">{{ `${totalBooked + equipment.available_quantity} Available from
          ${formatDate(nextAvailableDate)}` }}</p>
      </div>
      <div v-else class="text-red-600 mt-6">
        <p>Temporarily Unavailable</p>

      </div>

      <p class="availability mt-2 text-lg flex items-center">
        <span v-if="equipment.is_available" class="relative  text-green px-6 py-3 
           rounded-2xl font-bold shadow-xl border-2 border-gold-premium 
           transition-all duration-500 ease-in-out 
           flex items-center space-x-3 animate-availability premium-glass">
          <span class="flex items-center space-x-2">
            <span class="text-green-600 font-extrabold text-xl">
              {{ equipment.available_quantity }} Available Now
            </span>
            <i class="pi pi-verified premium-verified-icon"></i>
          </span>
        </span>
      </p>


    </div>

    <!-- Location -->
    <div class="address mb-4">
      <h2 class="text-xl font-semibold mb-2 border-b pb-2">Location:</h2>
      <p>{{ equipment.address?.street_address }}</p>
      <p v-if="equipment.address?.street_address2">{{ equipment.address.street_address2 }}</p>
      <p>{{ equipment.address?.city }}, {{ equipment.address?.state }} {{ equipment.address?.zip_code }}</p>
      <p>{{ equipment.address?.country }}</p>
    </div>

    <!-- Tags -->
    <div class="tags mb-4 border-b pb-2">
      <h3 class="text-lg font-semibold mb-2">Tags:</h3>
      <div class="flex flex-wrap gap-2" v-if="equipment.tags">
        <span v-for="tag in equipment.tags" :key="tag.name"
          class="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium">
          {{ tag.name }}
        </span>
      </div>
    </div>

    <!-- Booking Form -->
    <div class="booking-form p-4 border rounded-lg shadow-md bg-gray-50"
      v-if="authStore.user?.role !== 'lessor' && equipment.owner !== authStore.user?.id && !equipment.is_available">
      <form @submit.prevent="submitBooking">
        <div class="mb-4">
          <label for="start-date" class="block text-sm font-medium">Start Date:</label>
          <input type="date" id="start-date" v-model="startDate" :min="today" :disabled="isFullyBooked" required
            class="date-input w-full"
            :class="{ 'disabled-date': isDateBooked(startDate), 'partially-booked-date': isPartiallyBooked(startDate) }" />
          <p v-if="dateError" class="error-message">{{ dateError }}</p>
        </div>

        <div class="mb-4">
          <label for="end-date" class="block text-sm font-medium">End Date:</label>
          <input type="date" id="end-date" v-model="endDate" :min="startDate" :disabled="isFullyBooked" required
            class="date-input w-full"
            :class="{ 'disabled-date': isDateBooked(endDate), 'partially-booked-date': isPartiallyBooked(endDate) }" />
          <p v-if="dateError" class="error-message">{{ dateError }}</p>
        </div>

        <div class="mb-4">
          <label for="quantity" class="block text-sm font-medium">Number of Equipments:</label>
          <input type="number" id="quantity" v-model="quantity" min="1" :disabled="isFullyBooked"
            :max="equipment.available_quantity" @input="validateQuantity" required class="p-2 border rounded w-full" />
          <p v-if="quantityError" class="error-message">{{ quantityError }}</p>
        </div>

        <button type="submit"
          class="button add-to-cart bg-yellow-500 text-black py-2 px-4 rounded hover:bg-yellow-400 transition"
          :disabled="isFullyBooked">
          Add to Cart
        </button>
      </form>
    </div>

    <!-- Talk to Owner -->
    <RouterLink v-if="authStore.isAuthenticated && props.equipment.owner !== authStore.user.id"
      :to="{ path: '/profile', query: { section: 'chats' } }" @click="createChat"
      class="block mt-4 text-center text-blue-500 font-medium">
      Talk to Owner
    </RouterLink>
  </div>
</template>


<style>



/* 🌟 Glowing Gold Borders */
.border-gold-premium {
  border: 2px solid green;
  box-shadow: 0 0 12px rgba(255, 215, 0, 0.1);
}


.animate-availability {
  animation: goldPulse 1s infinite alternate ease-in-out;
}

/* 🏆 Premium Gold Button */
.btn-noir-gold {
  background: linear-gradient(90deg, #FFD700, #E6C200);
  color: #0D0D0D;
  font-weight: bold;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(255, 215, 0, 0.1);
}
.btn-noir-gold:hover {
  background: linear-gradient(90deg, #E6C200, #FFD700);
  box-shadow: 0 6px 24px rgba(255, 215, 0, 0.7);
}


/* Date Input Styling */
.date-input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  transition: 0.2s ease-in-out;
}

.date-input:focus {
  border-color: #ffcc00;
  box-shadow: 0 0 5px rgba(255, 204, 0, 0.5);
}

.disabled-date {
  pointer-events: none;
  opacity: 0.5;
  background-color: #f8d7da;
  color: #721c24;
}

.partially-booked-date {
  background-color: #fff3cd;
  color: #856404;
}

.error-message {
  color: red;
  font-size: 0.875rem;
  margin-top: .5rem;
  margin-bottom: 1rem;
}

.booking-item {
  background-color: #f3f4f6;
  padding: 8px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.add-to-cart {
  width: 100%;
  text-align: center;
  font-weight: bold;
}
</style>


<script setup>
// filepath: /home/techbro/Desktop/usenlease/frontend/src/components/EquipmentDetails.vue
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useCartStore } from '@/store/cart';
import useNotifications from '@/store/notification';
import axios from 'axios';
import { useChatStore } from '@/store/chat';
import { useRoute } from 'vue-router';  // Import useRoute to access route parameters

const route = useRoute();  // Get the current route object

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
const totalBooked = ref(0);  // New ref to store total booked items

const items_data = ref(null);

const today = new Date().toISOString().split('T')[0];

const isFullyBooked = computed(() => props.equipment.available_quantity === 0);

const equipmentId = route.params.id;

const createChat = async () => {
  const recepient = props.equipment.owner;
  const chat = await chatStore.createChat(recepient, props.equipment);
};

const formatDate = (date) => {
  if (!date) return "Unavailable";
  const options = { year: "numeric", month: "short", day: "numeric" };
  return new Date(date).toLocaleDateString(undefined, options);
};

const fetchTotalBookedItems = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/order-items/${equipmentId}/total-booked/`);
    totalBooked.value = response.data.total_booked;
    console.log("Booked Dates with quantity:", response.data.booked_dates);
    console.log("total booked", totalBooked.value);

    items_data.value = response.data.booked_dates;
  } catch (error) {
    showNotification('Failed to fetch booked items', `Error: ${error.response?.data.error || error.response?.data.detail || error}`, 'error');
  }
};

// Fetch total booked items when the component is mounted
onMounted(() => {
  fetchTotalBookedItems();
});

const isDateRangePartiallyBooked = (start, end, quantity) => {
  let totalBookedCount = totalBooked.value;

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
      totalBookedCount++;
    }
  }

  // Check if the remaining quantity after booking is sufficient
  return totalBookedCount + quantity > props.equipment.available_quantity;
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

const availableForPartialBooking = computed(() => {
  // Calculate the partially available quantity by checking the booked ranges
  let totalBookedCount = totalBooked.value;
  let totalAvailableForPartial = props.equipment.available_quantity;

  props.equipment.booked_dates.forEach((range) => {
    const bookedStart = new Date(range.start_date);
    const bookedEnd = new Date(range.end_date);

    // Check if the equipment is partially booked within a given range
    const now = new Date();
    if (bookedStart <= now && bookedEnd >= now) {
      totalBookedCount++;
    }
  });

  totalAvailableForPartial -= totalBookedCount;

  return totalAvailableForPartial > 0 ? totalAvailableForPartial : 0;
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

  return availablePeriods.length > 0 ? `Available between: ${availablePeriods.join(', ')}` : '';
});
</script>
