<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';

// Router and store
const router = useRouter();
const store = useEquipmentsStore();

// Local state
const isLoading = ref(false); // Unified loading state for all fetch operations
const hasFetchedInitial = ref(false); // Track if initial fetch has occurred

// Fetch data on mount
onMounted(async () => {
  isLoading.value = true;
  try {
    await Promise.all([
      store.fetchEquipments(), // Uses store.pageSize, fetches first page
      store.fetchCategories(),
    ]);
    hasFetchedInitial.value = true;
  } catch (error) {
    // Store handles notifications via showNotification
  } finally {
    isLoading.value = false;
  }
});

// Sync page size with store
const pageSize = computed({
  get: () => store.pageSize,
  set: (value) => {
    store.setPageSize(value);
  },
});

// Watch pageSize changes
watch(
  () => store.pageSize,
  async () => {
    isLoading.value = true;
    try {
      await store.fetchEquipments(); // Refetch with new page size
    } catch (error) {
      // Store handles notifications
    } finally {
      isLoading.value = false;
    }
  },
  { immediate: false }
);

// Computed properties from store
const equipments = computed(() => store.equipments);
const totalPages = computed(() => store.totalPages);
const pageLinks = computed(() => store.pageLinks);
const previousPageUrl = computed(() => store.previousPageUrl);
const nextPageUrl = computed(() => store.nextPageUrl);
const currentPage = computed(() => store.currentPage);

// Navigation functions
const fetchPage = async (pageUrl) => {
  if (pageUrl) {
    isLoading.value = true;
    try {
      await store.fetchPage(pageUrl);
    } catch (error) {
      // Store handles notifications
    } finally {
      isLoading.value = false;
    }
  }
};

const fetchNextPage = async () => {
  isLoading.value = true;
  try {
    await store.fetchNextPage();
  } catch (error) {
    // Store handles notifications
  } finally {
    isLoading.value = false;
  }
};

const fetchPreviousPage = async () => {
  isLoading.value = true;
  try {
    await store.fetchPreviousPage();
  } catch (error) {
    // Store handles notifications
  } finally {
    isLoading.value = false;
  }
};

const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({
      name: 'equipment-details',
      params: {
        id: encodeURIComponent(equipmentId), // Security
      },
    });
  }
};

// Utility to render star ratings
const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(5 - fullStars - halfStar);
};

// Watch equipments to reset loading if data arrives
watch(
  () => store.equipments.length,
  (newLength) => {
    if (newLength > 0 && isLoading.value) {
      isLoading.value = false;
    }
  }
);
</script>

<template>
  <div class="container mx-auto p-4">
    <!-- Enhanced Loading State -->
    <div
      v-if="isLoading"
      class="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-[100] transition-opacity duration-300"
      role="status"
      aria-live="polite"
      aria-label="Loading equipment"
    >
      <div
        class="bg-white p-10 rounded-2xl shadow-xl flex flex-col items-center max-w-md mx-4 transform transition-all duration-300 animate-fade-in border border-gray-200"
      >
        <!-- Animated Dots Loader -->
        <div class="flex space-x-2 mb-4">
          <span class="w-3 h-3 bg-[#ff6f00] rounded-full animate-bounce"></span>
          <span class="w-3 h-3 bg-[#ff9e00] rounded-full animate-bounce animation-delay-150"></span>
          <span class="w-3 h-3 bg-[#ffc400] rounded-full animate-bounce animation-delay-300"></span>
        </div>
        <!-- Loading text -->
        <p class="text-sm text-gray-600 tracking-wide font-medium">
          Rent or Lease Anything You Need...
        </p>
      </div>
    </div>

    <!-- Page Size Selection -->
    <div v-if="!isLoading || equipments.length > 0" class="mb-4 flex justify-end items-center">
      <label for="pageSizeSelect" class="mr-2 text-sm font-semibold text-gray-700">Items per page:</label>
      <select
        id="pageSizeSelect"
        v-model="pageSize"
        class="border rounded p-1 text-sm bg-white focus:ring-2 focus:ring-[#ff6f00] focus:border-[#ff6f00] transition"
        aria-label="Select number of items per page"
      >
        <option v-for="size in [10, 20, 30, 50]" :key="size" :value="size">
          {{ size }}
        </option>
      </select>
    </div>

    <!-- Equipment Grid -->
    <div class="scrollable-container">
      <div
        v-if="equipments.length > 0"
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-4"
        role="list"
        aria-label="List of equipment"
      >
        <div
          v-for="equipment in equipments"
          :key="equipment.id"
          class="bg-white rounded-lg shadow-md overflow-hidden transition-all hover:shadow-lg cursor-pointer border border-gray-100"
          role="listitem"
          :aria-label="`Equipment: ${equipment.name}`"
          @click="goToDetail(equipment.id)"
        >
          <div class="relative aspect-square">
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
            <img
              v-if="equipment.images && equipment.images.length > 0"
              :src="equipment.images[0].image_url"
              :alt="equipment.name"
              class="w-full h-full object-cover"
              loading="lazy"
            />
            <div
              v-else
              class="w-full h-full bg-gray-100 flex items-center justify-center"
            >
              <i class="pi pi-image text-4xl text-gray-400"></i>
            </div>
          </div>

          <div class="p-3">
            <h3
              class="text-sm font-semibold mb-1 text-gray-900 line-clamp-2"
              :title="equipment.name"
            >
              {{ store.truncateText(equipment.name, 20) }}
            </h3>
            <p class="text-gray-600 text-xs mb-2">
              <span class="font-medium">${{ equipment.hourly_rate }}</span> / day
            </p>
            <div class="flex items-center mb-2">
              <span class="rating text-yellow-500 mr-1 text-xs sm:text-sm">{{
                renderStars(equipment.rating)
              }}</span>
              <span class="reviews text-gray-600 text-[10px] sm:text-xs">
                ({{ equipment.equipment_reviews?.length || 0 }})
              </span>
            </div>
            <button
              @click.stop="goToDetail(equipment.id)"
              class="w-full bg-[#ff6f00] rounded text-white text-xs px-3 py-2 mt-2 transition-colors duration-200 hover:bg-[#ff9e00] focus:outline-none focus:ring-2 focus:ring-[#ff6f00] focus:ring-opacity-50"
              aria-label="Rent this equipment"
            >
              Rent Now
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="hasFetchedInitial && !isLoading && equipments.length === 0"
        class="text-center py-16 bg-gray-50 rounded-lg"
        aria-live="polite"
      >
        <i class="pi pi-inbox text-6xl text-gray-400"></i>
        <h3 class="text-xl text-gray-600 mt-4">No equipment available</h3>
        <p class="text-gray-500 mt-2">Please check back later or try different filters</p>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div
      v-if="totalPages > 1 && !isLoading && equipments.length > 0"
      class="pagination flex justify-center mt-8"
      aria-label="Pagination"
    >
      <button
        :disabled="!previousPageUrl"
        @click="fetchPreviousPage"
        class="px-4 py-2 mx-1 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors"
        aria-label="Previous page"
        :aria-disabled="!previousPageUrl"
      >
        Previous
      </button>

      <template v-for="page in pageLinks" :key="page.url">
        <button
          @click="fetchPage(page.url)"
          class="px-4 py-2 mx-1 rounded-lg text-sm min-w-[40px] transition-colors"
          :class="page.page === currentPage ? 'bg-black text-white' : 'bg-yellow-500 hover:bg-gray-300'"
          :aria-label="`Go to page ${page.page}`"
          :aria-current="page.page === currentPage ? 'page' : null"
        >
          {{ page.page }}
        </button>
      </template>

      <button
        :disabled="!nextPageUrl"
        @click="fetchNextPage"
        class="px-4 py-2 mx-1 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors"
        aria-label="Next page"
        :aria-disabled="!nextPageUrl"
      >
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
.scrollable-container {
  max-height: calc(100vh - 200px);
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

/* Focus styles for accessibility */
button:focus,
select:focus {
  outline: 2px solid #ff9e00;
  outline-offset: 2px;
}

/* Transition for smoother hover effects */
[class*="hover:"] {
  transition: all 0.2s ease;
}

/* Fade-in animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

/* Animated dots bouncing */
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

/* Delay animations for a cascading effect */
.animation-delay-150 {
  animation-delay: 0.15s;
}
.animation-delay-300 {
  animation-delay: 0.3s;
}
</style>