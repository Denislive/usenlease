<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';

const router = useRouter();
const store = useEquipmentsStore();
const currentPage = ref(1);

onMounted(async () => {
  await store.fetchEquipments();
  await store.fetchCategories();
});

const itemsPerPage = computed(() => {
  return window.innerWidth >= 768 ? 64 : 32; // 64 on medium up, 32 below
});

// Watch for window resize to update itemsPerPage dynamically
const updateItemsPerPage = () => {
  currentPage.value = 1; // Reset to first page on resize
};
window.addEventListener('resize', updateItemsPerPage);

const paginatedEquipments = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage.value;
  const endIndex = startIndex + itemsPerPage.value;
  return store.filteredEquipments.slice(startIndex, endIndex);
});

const totalPages = computed(() => Math.ceil(store.filteredEquipments.length / itemsPerPage.value));

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  }
};
</script>

<template>
  <div class="container mx-auto p-4">
    <!-- Equipment Grid -->
    <div class="scrollable-container">
      <div class="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6">
        <div
          v-for="equipment in paginatedEquipments"
          :key="equipment.id"
          class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer"
        >
          <div class="relative">
            <span
              v-if="equipment.is_available"
              class="absolute top-0 left-0 bg-green-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded"
            >
              Available
            </span>
            <span
              v-else
              class="absolute top-0 left-0 bg-blue-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded"
              @click="goToDetail(equipment.id)"
            >
              Click to check details
            </span>

            <img
              v-if="equipment.images.length > 0"
              :src="equipment.images[0].image_url"
              alt="Equipment Image"
              class="w-full h-32 lg:h-48 object-contain"
            />
            <img
              v-else
              src="https://via.placeholder.com/350"
              alt="Placeholder Image"
              class="w-full h-32 object-contain"
            />
          </div>

          <div class="p-4">
            <h5 class="text-sm sm:text-base font-semibold mb-1 text-gray-900">
              {{ store.truncateText(equipment.name, 20) }}
            </h5>
            <p class="text-gray-600 text-xs sm:text-sm mb-2">{{ equipment.hourly_rate }} / Day</p>
            <button 
              @click="goToDetail(equipment.id)" 
              class="bg-[#ff6f00] rounded text-white text-xs sm:text-sm px-3 sm:px-4 py-1 sm:py-2 mt-2 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110"
            >
              Rent Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty List Message -->
    <div v-if="store.filteredEquipments.length === 0" class="text-center py-16">
      <i class="pi pi-exclamation-circle text-6xl sm:text-9xl text-gray-500"></i>
      <p class="text-lg sm:text-xl text-gray-500 mt-4">Oops! No items here!</p>
      <p class="text-base sm:text-xl text-gray-500 mt-4">Try adding a new item by hitting the lease button.</p>
    </div>

    <!-- Pagination -->
    <div class="pagination flex justify-center mt-4" v-if="totalPages > 1">
      <button
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 text-xs sm:text-sm"
      >
        Previous
      </button>

      <button
        v-for="page in totalPages"
        :key="page"
        @click="goToPage(page)"
        :class="{
          'bg-[#1c1c1c] text-white': page === currentPage,
          'bg-[#ffc107] hover:bg-gray-300': page !== currentPage
        }"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 rounded text-xs sm:text-sm"
      >
        {{ page }}
      </button>

      <button
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
        class="px-3 sm:px-4 py-1 sm:py-2 mx-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 text-xs sm:text-sm"
      >
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Scrollable section */
.scrollable-container {
  max-height: 80vh;
  overflow-y: auto;
}
</style>
