<script setup>
defineProps({
  equipments: {
    type: Array,
    required: true
  }
});
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';

const router = useRouter();
const store = useEquipmentsStore();
const currentPage = ref(1);
const pageSize = ref(store.pageSize || 10); // Default page size
const isLoading = ref(false);

// Fetch data on mount with error handling
onMounted(async () => {
  try {
    isLoading.value = true;
    await Promise.all([
      store.fetchEquipments(currentPage.value, pageSize.value),
      store.fetchCategories()
    ]);
  } catch (error) {
    // Consider adding user notification here
  } finally {
    isLoading.value = false;
  }
});

// Watch page size and update data with debounce
let debounceTimer;
watch(pageSize, async (newSize) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    if (newSize !== store.pageSize) {
      try {
        isLoading.value = true;
        currentPage.value = 1;
        store.setPageSize(newSize);
        await store.fetchEquipments(currentPage.value, newSize);
      } catch (error) {
      } finally {
        isLoading.value = false;
      }
    }
  }, 300); // 300ms debounce
});

// Computed properties
const equipments = computed(() => store.equipments);
const totalPages = computed(() => store.totalPages);
const pageLinks = computed(() => store.pageLinks);
const previousPageUrl = computed(() => store.previousPageUrl);
const nextPageUrl = computed(() => store.nextPageUrl);

// Navigation functions with validation
const goToPage = async (page) => {
  if (page >= 1 && page <= totalPages.value) {
    try {
      isLoading.value = true;
      currentPage.value = page;
      await store.fetchEquipments(page, pageSize.value);
    } catch (error) {
    } finally {
      isLoading.value = false;
    }
  }
};

const fetchPage = async (pageUrl) => {
  if (pageUrl) {
    try {
      isLoading.value = true;
      await store.fetchPage(pageUrl);
    } catch (error) {
    } finally {
      isLoading.value = false;
    }
  }
};

const goToDetail = (equipmentId) => {
  if (equipmentId && typeof equipmentId === 'string') {
    router.push({ 
      name: 'equipment-details', 
      params: { 
        id: encodeURIComponent(equipmentId) // Security: encode URI component
      } 
    });
  }
};

const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(5 - fullStars - halfStar);
};
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

    <!-- Loading text with a subtle animation -->
    <p class="text-sm text-gray-600 tracking-wide font-medium">
      Loading items, please wait...
    </p>
  </div>
</div>


    <!-- Page Size Selection -->
    <div class="mb-4 flex justify-end items-center">
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
              v-if="equipment.images.length > 0"
              :src="equipment.images[0].image_url"
              :alt="`Image of ${equipment.name}`"
              class="w-full h-full object-cover"
              loading="lazy"
              @click="goToDetail(equipment.id)"
            />
            <img
              v-else
              src="https://via.placeholder.com/350"
              :alt="`${equipment.category}-${equipment.name}`"
              class="w-full h-full object-cover"
              loading="lazy"
              @click="goToDetail(equipment.id)"
            />
          </div>

          <div class="p-3">
            <h3 class="text-sm font-semibold mb-1 text-gray-900 line-clamp-2" :title="equipment.name">
              {{ store.truncateText(equipment.name, 20) }}
            </h3>
            <p class="text-gray-600 text-xs mb-2">
              <span class="font-medium">${{ equipment.hourly_rate }}</span> / day
            </p>
            <div class="flex items-center mb-2">
              <span class="rating text-yellow-500 mr-1 text-xs sm:text-sm">{{ renderStars(equipment.rating) }}</span>
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
        v-else-if="!isLoading"
        class="text-center py-16 bg-gray-50 rounded-lg"
        aria-live="polite"
      >
        <i class="pi pi-exclamation-circle text-6xl text-gray-400"></i>
        <h3 class="text-xl text-gray-600 mt-4">No equipment available</h3>
        <p class="text-gray-500 mt-2">Please check back later or try different filters</p>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div 
      v-if="totalPages > 1 && !isLoading"
      class="pagination flex justify-center mt-8"
      aria-label="Pagination"
    >
      <button 
        :disabled="!previousPageUrl" 
        @click="fetchPage(previousPageUrl)"
        class="px-4 py-2 mx-1 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors"
        aria-label="Previous page"
      >
        Previous
      </button>

      <template v-for="page in pageLinks" :key="page.url">
        <button 
          v-if="page.page !== '...'"
          @click="fetchPage(page.url)"
          class="px-4 py-2 mx-1 rounded-lg text-sm min-w-[40px] transition-colors"
          :class="page.page === currentPage ? 'bg-[#ff6f00] text-white' : 'bg-gray-100 hover:bg-gray-200'"
          :aria-label="`Go to page ${page.page}`"
          :aria-current="page.page === currentPage ? 'page' : null"
        >
          {{ page.page }}
        </button>
        <span 
          v-else
          class="px-1 mx-1 flex items-end"
          aria-hidden="true"
        >
          ...
        </span>
      </template>

      <button 
        :disabled="!nextPageUrl" 
        @click="fetchPage(nextPageUrl)"
        class="px-4 py-2 mx-1 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors"
        aria-label="Next page"
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
button:focus, select:focus {
  outline: 2px solid #ff9e00;
  outline-offset: 2px;
}

/* Transition for smoother hover effects */
[class*="hover:"] {
  transition: all 0.2s ease;
}


/* Fade-in animation */
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
.animate-fade-in { animation: fadeIn 0.3s ease-out; }

/* Animated dots bouncing */
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}
.animate-bounce { animation: bounce 1.2s infinite ease-in-out; }

/* Delay animations for a cascading effect */
.animation-delay-150 { animation-delay: 0.15s; }
.animation-delay-300 { animation-delay: 0.3s; }
</style>