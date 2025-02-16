<script setup>
import { defineProps, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';

const props = defineProps({
  equipments: {
    type: Array,
    required: true,
  },
});


const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  const emptyStars = 5 - fullStars - halfStar;

  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(emptyStars);
};

const router = useRouter();
const store = useEquipmentsStore();


onMounted(async () => {
  await store.fetchCategories();
});


const categories = store.categories.value;

const itemsPerPage = 20; // Items per page
const currentPage = ref(1); // Current page number

// Paginated Equipments
const paginatedEquipments = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return props.equipments.slice(startIndex, endIndex);
});

// Total Pages
const totalPages = computed(() => Math.ceil(props.equipments.length / itemsPerPage));

// Navigate to a specific page
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
    <!-- Scrollable Equipment Grid -->
    <div class="scrollable-container">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
        <div
          v-for="equipment in paginatedEquipments"
          :key="equipment.id"
          class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer"
        >
          <div class="relative">
            <span :class="{
              'bg-green-500': equipment.is_available,
              'bg-blue-500': !equipment.is_available
            }" class="absolute top-0 left-0 text-white text-xs font-bold px-2 py-1 rounded flex items-center">
              <i :class="{
                'pi pi-check-circle': equipment.is_available,
                'pi pi-info-circle': !equipment.is_available
              }" class="mr-1"></i>
              <div v-if="equipment.is_available" class="mr-1">
                {{ equipment.available_quantity }}
              </div>
              {{ equipment.is_available ? 'Available' : 'Click to Check details' }}
            </span>

            <img v-if="equipment.images.length > 0" :src="equipment.images[0].image_url"
            :alt="equipment.images.length ? equipment.name : 'Placeholder Image'"  class="w-full h-48 object-contain" />
            <img v-else src="https://via.placeholder.com/350" alt="Placeholder Image" class="w-full h-48 object-contain" />
          </div>

          <div class="p-4">
            <h5 class="text-sm font-semibold mb-1 text-gray-900">
              {{ store.truncateText(equipment.name, 20) }}
            </h5>
            <p class="text-gray-600 mb-2">{{ equipment.hourly_rate }} / Day</p>
            <div class="flex items-center mb-2">
              <span class="rating text-yellow-500 mr-1">{{ renderStars(equipment.rating) }}</span>
              <span class="reviews text-gray-600 text-xs">
                ({{ equipment.equipment_reviews ? equipment.equipment_reviews.length : 0 }})
              </span>
            </div>
            <button 
              @click="goToDetail(equipment.id)" 
              class="bg-[#ff6f00] rounded text-white px-4 py-2 mt-2 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110">
              Rent Now
            </button>
          </div>
        </div>
        
      </div>
    </div>

    <div v-if="paginatedEquipments.length === 0" class="text-center py-16">
      <i class="pi pi-exclamation-circle text-9xl text-gray-500"></i>
      <p class="text-xl text-gray-500 mt-4">Oops!</p>
      <p class="text-xl text-gray-500 mt-4">Try other combinations of the item name, tags or location</p>
    </div>

    <!-- Pagination -->
    <div class="pagination flex justify-center mt-4" v-if="totalPages > 1">
      <button
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
        class="px-4 py-2 mx-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
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
        class="px-4 py-2 mx-1 rounded"
      >
        {{ page }}
      </button>

      <button
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
        class="px-4 py-2 mx-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
      >
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Scrollable section */
.scrollable-container {
  max-height: 500px; /* Adjust as needed */
  overflow-y: auto;
  padding-right: 10px; /* Prevents scroll bar overlap */
}
</style>
