<template>
  <div class="container mx-auto p-4">
  

    <!-- Loading State -->
    <div
      v-if="store.isLoading"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      role="status"
      aria-live="polite"
      aria-label="Loading equipment"
    >
      <div class="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
        <div class="flex space-x-2 mb-4">
          <span class="w-3 h-3 bg-[#ff6f00] rounded-full animate-bounce"></span>
          <span class="w-3 h-3 bg-[#ff9e00] rounded-full animate-bounce animation-delay-150"></span>
          <span class="w-3 h-3 bg-[#ffc400] rounded-full animate-bounce animation-delay-300"></span>
        </div>
        <p class="text-sm text-gray-600">Rent or Lease Anything You Need...</p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-if="store.error"
      class="mb-4 p-4 bg-red-100 text-red-700 rounded-lg"
      role="alert"
      aria-live="assertive"
    >
      {{ store.error }}
    </div>

    <!-- Scrollable Equipment Grid -->
    <div class="scrollable-container">
      <div
        v-if="store.equipments.length > 0"
        class="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6"
        role="list"
        aria-label="List of equipment"
      >
        <div
          v-for="equipment in store.equipments"
          :key="equipment.id"
          class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer"
          role="listitem"
          :aria-label="`Equipment: ${equipment.name}`"
        >
          <div class="relative">
            <span
              v-if="equipment.is_available"
              class="absolute top-0 left-0 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded z-10"
              aria-label="Available"
            >
              {{ equipment.available_quantity }} Available
            </span>
            <span
              v-else
              class="absolute top-0 left-0 bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded z-10"
              aria-label="Check details"
            >
              View Details
            </span>
            <div
              @click="goToDetail(equipment.id)"
              class="w-full h-32 lg:h-48 flex items-center justify-center rounded-t-lg bg-gray-100"
            >
              <img
                v-if="equipment.images?.length"
                :src="equipment.images[0].image_url"
                :alt="equipment.name"
                class="w-full h-full object-contain rounded-t-lg"
                loading="lazy"
              />
              <i v-else class="pi pi-image text-4xl text-gray-400"></i>
            </div>
          </div>

          <div class="p-1">
            <h5 class="text-sm font-semibold mb-1 text-gray-900">
              {{ store.truncateText(equipment.name, 20) }}
            </h5>
            <p class="text-gray-600 text-xs sm:text-sm mb-2">${{ equipment.hourly_rate }} / Day</p>
            <div class="flex items-center mb-2">
              <span class="rating text-yellow-500 mr-1 text-xs sm:text-sm">{{
                renderStars(equipment.rating)
              }}</span>
              <span class="reviews text-gray-600 text-[10px] sm:text-xs">
                ({{ equipment.equipment_reviews?.length || 0 }})
              </span>
            </div>
            <button
              @click="goToDetail(equipment.id)"
              class="w-full bg-[#ff6f00] rounded text-white text-xs sm:text-sm px-4 py-1 mt-2 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-[#ff6f00]"
              aria-label="Rent this equipment"
            >
              Rent Now
            </button>
          </div>
        </div>
      </div>

      <!-- Empty List Message -->
      <div
        v-else-if="!store.isLoading && !store.error"
        class="text-center py-16"
        aria-live="polite"
      >
        <i class="pi pi-inbox text-6xl sm:text-9xl text-gray-500"></i>
        <p class="text-lg sm:text-xl text-gray-500 mt-4">Oops! No items here!</p>
        <p class="text-base sm:text-xl text-gray-500 mt-4">
          Try adding a new item by hitting the lease button.
        </p>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div
      v-if="store.totalPages > 1 && !store.isLoading && store.equipments.length > 0"
      class="pagination flex justify-center mt-6"
      aria-label="Pagination"
    >
      <button
        :disabled="!store.previousPageUrl"
        @click="store.fetchPreviousPage"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm"
        aria-label="Previous page"
        :aria-disabled="!store.previousPageUrl"
      >
        Previous
      </button>

      <button
        v-for="page in store.pageLinks"
        :key="page.url"
        @click="store.fetchPage(page.url)"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 rounded-lg text-xs sm:text-sm"
        :class="page.page === store.currentPage ? 'bg-black text-white' : 'bg-yellow-500 hover:bg-gray-300'"
        :aria-label="`Go to page ${page.page}`"
        :aria-current="page.page === store.currentPage ? 'page' : null"
      >
        {{ page.page }}
      </button>

      <button
        :disabled="!store.nextPageUrl"
        @click="store.fetchNextPage"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm"
        aria-label="Next page"
        :aria-disabled="!store.nextPageUrl"
      >
        Next
      </button>
    </div>

    <Carousel />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';
import Carousel from './Carousels.vue';

const router = useRouter();
const store = useEquipmentsStore();

// Fetch categories on mount
onMounted(async () => {
  try {
    await store.fetchCategories();
    // Initial fetch is handled by store's watch on searchQuery/selectedCategories
  } catch (error) {
    // Store handles notifications via showNotification
  }
});

// Navigation to equipment details
const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  }
};

// Render star ratings
const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(5 - fullStars - halfStar);
};
</script>

<style scoped>
.scrollable-container {
  max-height: 80vh;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #ff6f00 #f1f1f1;
}

.scrollable-container::-webkit-scrollbar {
  width: 8px;
}

.scrollable-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.scrollable-container::-webkit-scrollbar-thumb {
  background-color: #ff6f00;
  border-radius: 10px;
}

.rounded {
  border-radius: 5px;
}

/* Focus styles for accessibility */
button:focus,
select:focus,
input:focus {
  outline: 2px solid #ff9e00;
  outline-offset: 2px;
}

/* Transition for smoother hover effects */
[class*="hover:"] {
  transition: all 0.3s ease;
}

/* Bounce animation for loading dots */
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
.animate-bounce {
  animation: bounce 1.2s infinite ease-in-out;
}
.animation-delay-150 {
  animation-delay: 0.15s;
}
.animation-delay-300 {
  animation-delay: 0.3s;
}
</style>