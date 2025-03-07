<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';

const router = useRouter();
const store = useEquipmentsStore();
const currentPage = ref(1);
const pageSize = ref(store.pageSize || 10); // Default page size

onMounted(async () => {
  await store.fetchEquipments(1, pageSize.value);
  await store.fetchCategories();
});

// Watch for changes in page size and fetch data accordingly
watch(pageSize, async (newSize) => {
  currentPage.value = 1;
  store.pageSize = newSize; // Update store with new page size
  await store.fetchEquipments(currentPage.value, newSize);
});

// Get paginated equipment list from the store
const equipments = computed(() => store.equipments);
const totalPages = computed(() => store.totalPages);

const goToPage = async (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    await store.fetchEquipments(page, pageSize.value);
  }
};

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
</script>

<template>
  <div class="container mx-auto p-4">
    <!-- Page Size Selection -->
    <div class="mb-4 flex justify-end">
      <label class="mr-2 text-sm font-semibold">Items per page:</label>
      <select v-model="pageSize" class="border rounded p-1 text-sm">
        <option v-for="size in [10, 20, 30, 50]" :key="size" :value="size">
          {{ size }}
        </option>
      </select>
    </div>

    <!-- Equipment Grid -->
    <div class="scrollable-container">
      <div class="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-2">
        <div
          v-for="equipment in equipments"
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

          <div class="p-1">
            <h5 class="text-sm font-semibold mb-1 text-gray-900">
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
    <div v-if="equipments.length === 0" class="text-center py-16">
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

<style scoped>
/* Scrollable section */
.scrollable-container {
  max-height: 80vh;
  overflow-y: auto;
}
</style>
