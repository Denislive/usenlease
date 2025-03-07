<template>
  <div class="container mx-auto p-4">
    <!-- Scrollable Equipment Grid -->
    <div class="scrollable-container">
      <div class="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6">
        <div
          v-for="equipment in store.equipments"
          :key="equipment.id"
          class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer"
        >
          <div class="relative">
            <span
              v-if="equipment.is_available"
              class="absolute top-0 left-0 bg-green-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded flex items-center"
            >
              <i class="pi pi-check-circle mr-1"></i>
              <div class="mr-1">{{ equipment.available_quantity }}</div>
              Available
            </span>
            <span
              v-else
              class="absolute top-0 left-0 bg-blue-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded flex items-center"
              @click="goToDetail(equipment.id)"
            >
              <i class="pi pi-info-circle mr-1"></i>
              Click to check details
            </span>
          </div>

          <img 
            :src="equipment.images.length ? equipment.images[0].image_url : 'https://via.placeholder.com/350'" 
            :alt="equipment.images.length ? equipment.name : 'Placeholder Image'" 
            class="w-full h-32 lg:h-48 object-contain rounded-t-lg" 
          />

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
              class="bg-[#ff6f00] rounded text-white text-xs sm:text-sm px-2 py-1 mt-2 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110">
              Rent Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty List Message -->
    <div v-if="store.equipments.length === 0" class="text-center py-16">
      <i class="pi pi-exclamation-circle text-6xl sm:text-9xl text-gray-500"></i>
      <p class="text-lg sm:text-xl text-gray-500 mt-4">Oops! No items here!</p>
      <p class="text-base sm:text-xl text-gray-500 mt-4">Try adding a new item by hitting the lease button.</p>
    </div>

    <!-- Pagination Controls -->
    <div v-if="store.totalPages" class="pagination flex justify-center mt-6">
      <button 
        :disabled="!store.previousPageUrl" 
        @click="fetchPage(store.previousPageUrl)"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 text-xs sm:text-sm">
        Previous
      </button>

      <button 
        v-for="page in store.pageLinks" :key="page.url" 
        @click="fetchPage(page.url)"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 rounded-lg text-xs sm:text-sm"
        :class="page.page === store.currentPage ? 'bg-black text-white' : 'bg-yellow-500 hover:bg-gray-300'">
        {{ page.page }}
      </button>

      <button 
        :disabled="!store.nextPageUrl" 
        @click="fetchPage(store.nextPageUrl)"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 text-xs sm:text-sm">
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';

const router = useRouter();
const store = useEquipmentsStore();

onMounted(async () => {
  await store.fetchEquipments();
  await store.fetchCategories();
});

const fetchPage = (pageUrl) => {
  if (pageUrl) {
    store.fetchPage(pageUrl);
  }
};

const goToDetail = (equipmentId) => {
  if (equipmentId) {
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
</style>
