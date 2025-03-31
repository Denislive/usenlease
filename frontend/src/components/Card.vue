<template>
  <div class="container mx-auto p-4">
    <!-- Loading State -->
    <div 
      v-if="isLoading && !initialLoadComplete"
      class="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-[100]"
    >
      <div class="bg-white p-10 rounded-2xl shadow-xl flex flex-col items-center max-w-md mx-4">
        <div class="flex space-x-2 mb-4">
          <span class="w-3 h-3 bg-[#ff6f00] rounded-full animate-bounce"></span>
          <span class="w-3 h-3 bg-[#ff9e00] rounded-full animate-bounce animation-delay-150"></span>
          <span class="w-3 h-3 bg-[#ffc400] rounded-full animate-bounce animation-delay-300"></span>
        </div>
        <p class="text-sm text-gray-600 tracking-wide font-medium">
          Lease or Rent Anything You Need...
        </p>
      </div>
    </div>

    <!-- Content Area -->
    <div v-show="initialLoadComplete">
      <!-- Page Size Selection -->
      <div class="mb-4 flex justify-end items-center">
        <label for="pageSizeSelect" class="mr-2 text-sm font-semibold text-gray-700">Items per page:</label>
        <select 
          id="pageSizeSelect"
          v-model="pageSize" 
          class="border rounded p-1 text-sm bg-white focus:ring-2 focus:ring-[#ff6f00] focus:border-[#ff6f00] transition"
        >
          <option v-for="size in [10, 20, 30, 50]" :key="size" :value="size">
            {{ size }}
          </option>
        </select>
      </div>

      <!-- Equipment Grid -->
      <div class="scrollable-container">
        <!-- Show equipment if available -->
        <div 
          v-if="equipments.length > 0"
          class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-4"
        >
          <div
            v-for="equipment in equipments"
            :key="equipment.id"
            class="bg-white rounded-lg shadow-md overflow-hidden transition-all hover:shadow-lg cursor-pointer border border-gray-100"
            @click="goToDetail(equipment.id)"
          >
            <!-- Image Section -->
            <div class="relative aspect-square">
              <span
                v-if="equipment.is_available"
                class="absolute top-0 left-0 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded z-10"
              >
                {{ equipment.available_quantity }} Available
              </span>
              <span
                v-else
                class="absolute top-0 left-0 bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded z-10"
              >
                View Details
              </span>
              <img
                v-if="equipment.images && equipment.images.length > 0"
                :src="equipment.images[0].image_url"
                :alt="`Image of ${equipment.name}`"
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

            <!-- Content Section -->
            <div class="p-3">
              <h3 class="text-sm font-semibold mb-1 text-gray-900 line-clamp-2">
                {{ equipment.name }}
              </h3>
              <p class="text-gray-600 text-xs mb-2">
                <span class="font-medium">${{ equipment.hourly_rate }}</span> / day
              </p>
              <div class="flex items-center mb-2">
                <span class="rating text-yellow-500 mr-1 text-xs sm:text-sm">
                  {{ renderStars(equipment.rating) }}
                </span>
                <span class="reviews text-gray-600 text-[10px] sm:text-xs">
                  ({{ equipment.equipment_reviews?.length || 0 }})
                </span>
              </div>
              <button 
                @click.stop="goToDetail(equipment.id)"
                class="w-full bg-[#ff6f00] rounded text-white text-xs px-3 py-2 mt-2 transition-colors duration-200 hover:bg-[#ff9e00]"
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
      >
        <button 
          :disabled="!previousPageUrl" 
          @click="fetchPage(previousPageUrl)"
          class="px-4 py-2 mx-1 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors"
        >
          Previous
        </button>

        <template v-for="page in pageLinks" :key="page.url">
          <button 
            v-if="page.page !== '...'"
            @click="fetchPage(page.url)"
            class="px-4 py-2 mx-1 rounded-lg text-sm min-w-[40px] transition-colors"
            :class="page.page === currentPage ? 'bg-[#ff6f00] text-white' : 'bg-gray-100 hover:bg-gray-200'"
          >
            {{ page.page }}
          </button>
          <span 
            v-else
            class="px-1 mx-1 flex items-end"
          >
            ...
          </span>
        </template>

        <button 
          :disabled="!nextPageUrl" 
          @click="fetchPage(nextPageUrl)"
          class="px-4 py-2 mx-1 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Loading indicator for subsequent loads -->
    <div 
      v-if="isLoading && initialLoadComplete"
      class="fixed bottom-4 right-4 bg-white p-3 rounded-lg shadow-lg flex items-center z-50"
    >
      <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-[#ff6f00] mr-2"></div>
      <span class="text-sm">Loading...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';

const router = useRouter();
const store = useEquipmentsStore();
const currentPage = ref(1);
const pageSize = ref(store.pageSize || 10);
const isLoading = ref(false);
const initialLoadComplete = ref(false);

// Fetch data on mount with error handling
onMounted(async () => {
  try {
    isLoading.value = true;
    await Promise.all([
      store.fetchEquipments(currentPage.value, pageSize.value),
      store.fetchCategories()
    ]);
    initialLoadComplete.value = true;
  } catch (error) {
    console.error("Error loading equipment:", error);
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
        console.error("Error changing page size:", error);
      } finally {
        isLoading.value = false;
      }
    }
  }, 300);
});

// Computed properties
const equipments = computed(() => store.equipments || []);
const totalPages = computed(() => store.totalPages || 0);
const pageLinks = computed(() => store.pageLinks || []);
const previousPageUrl = computed(() => store.previousPageUrl);
const nextPageUrl = computed(() => store.nextPageUrl);

// Navigation functions
const goToPage = async (page) => {
  if (page >= 1 && page <= totalPages.value) {
    try {
      isLoading.value = true;
      currentPage.value = page;
      await store.fetchEquipments(page, pageSize.value);
    } catch (error) {
      console.error("Error changing page:", error);
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
      console.error("Error fetching page:", error);
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
        id: encodeURIComponent(equipmentId)
      } 
    });
  }
};

const renderStars = (rating) => {
  rating = rating || 0; // Default to 0 if undefined
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(5 - fullStars - halfStar);
};
</script>

<style scoped>
.scrollable-container {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

/* Animation styles */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
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

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.aspect-square {
  aspect-ratio: 1/1;
}
</style>