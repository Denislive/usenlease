<template>
  <div class="container mx-auto p-4">
    <!-- Loading Overlay -->
    <div 
      v-if="isLoading"
      class="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <div class="bg-white p-4 rounded-lg shadow-lg flex items-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#ff6f00] mr-3"></div>
        <span class="text-gray-700">Loading...</span>
      </div>
    </div>

    <!-- Scrollable Equipment Grid -->
    <div class="scrollable-container relative">
      <div class="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6">
        <div
          v-for="equipment in store.equipments"
          :key="equipment.id"
          class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer"
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
            <img 
              :src="equipment.images.length ? equipment.images[0].image_url : 'https://via.placeholder.com/350'" 
              :alt="equipment.images.length ? equipment.name : 'Placeholder Image'" 
              class="w-full h-32 lg:h-48 object-contain rounded-t-lg" 
              @click="goToDetail(equipment.id)"
            />
          </div>

          <div class="p-1">
            <h5 class="text-sm font-semibold mb-1 text-gray-900">
              {{ store.truncateText(equipment.name, 20) }}
            </h5>
            <p class="text-gray-600 text-xs sm:text-sm mb-2">${{ equipment.hourly_rate }} / Day</p>
            <div class="flex items-center mb-2">
              <span class="rating text-yellow-500 mr-1 text-xs sm:text-sm">{{ renderStars(equipment.rating) }}</span>
              <span class="reviews text-gray-600 text-[10px] sm:text-xs">
                ({{ equipment.equipment_reviews?.length || 0 }})
              </span>
            </div>
            <button 
              @click="goToDetail(equipment.id)" 
              class="w-full bg-[#ff6f00] rounded text-white text-xs sm:text-sm px-4 py-1 mt-2 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110">
              Rent Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty List Message -->
    <div v-if="store.equipments.length === 0 && !isLoading" class="text-center py-16">
      <i class="pi pi-exclamation-circle text-6xl sm:text-9xl text-gray-500"></i>
      <p class="text-lg sm:text-xl text-gray-500 mt-4">Oops! No items here!</p>
      <p class="text-base sm:text-xl text-gray-500 mt-4">Try adding a new item by hitting the lease button.</p>
    </div>

    <!-- Pagination Controls -->
    <div v-if="store.totalPages" class="pagination flex justify-center mt-6">
      <button 
        :disabled="!store.previousPageUrl || isLoading" 
        @click="fetchPage(store.previousPageUrl)"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm transition-colors"
      >
        Previous
      </button>

      <button 
        v-for="page in store.pageLinks" 
        :key="page.url" 
        @click="fetchPage(page.url)"
        :disabled="isLoading"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 rounded-lg text-xs sm:text-sm transition-colors"
        :class="{
          'bg-black text-white': page.page === store.currentPage,
          'bg-yellow-500 hover:bg-gray-300': page.page !== store.currentPage,
          'opacity-50 cursor-not-allowed': isLoading
        }"
      >
        {{ page.page }}
      </button>

      <button 
        :disabled="!store.nextPageUrl || isLoading" 
        @click="fetchPage(store.nextPageUrl)"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm transition-colors"
      >
        Next
      </button>
    </div>
  </div>
  <Carousel />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';
import Carousel from './Carousels.vue';

const router = useRouter();
const store = useEquipmentsStore();
const isLoading = ref(false);

const selectedCategory = computed(() => store.selectedCategory);
const searchQuery = computed(() => store.searchQuery);

onMounted(async () => {
  try {
    isLoading.value = true;
    await store.fetchCategories();
    await fetchEquipmentsData();
  } catch (error) {
    console.error("Error loading data:", error);
  } finally {
    isLoading.value = false;
  }
});

const fetchEquipmentsData = async () => {
  try {
    isLoading.value = true;
    const filters = {
      category: selectedCategory.value === 'All' ? '' : selectedCategory.value,
      search: searchQuery.value,
    };
    await store.fetchFilteredEquipments(filters);
  } catch (error) {
    console.error("Error fetching equipment:", error);
  } finally {
    isLoading.value = false;
  }
};

const fetchPage = async (pageUrl) => {
  if (pageUrl && !isLoading.value) {
    try {
      isLoading.value = true;
      await store.fetchPage(pageUrl, {
        category: selectedCategory.value === 'All' ? '' : selectedCategory.value,
        search: searchQuery.value,
      });
    } catch (error) {
      console.error("Error changing page:", error);
    } finally {
      isLoading.value = false;
    }
  }
};

const goToDetail = (equipmentId) => {
  if (equipmentId && !isLoading.value) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  }
};

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
}
.rounded {
  border-radius: 5px;
}

/* Animation styles */
@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin {
  animation: spin 1s linear infinite;
}

/* Transition effects */
.transition-colors {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
</style>