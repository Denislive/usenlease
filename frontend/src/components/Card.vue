<script setup>
import { defineProps, ref, computed } from 'vue';
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
          @click="() => { goToDetail(equipment.id) }"
          class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer"
        >
          <div class="relative">
            <span :class="{
              'bg-green-500': equipment.is_available,
              'bg-red-500': !equipment.is_available
            }" class="absolute top-0 left-0 text-white text-xs font-bold px-2 py-1 rounded flex items-center">
              <i :class="{
                'pi pi-check-circle': equipment.is_available,
                'pi pi-times-circle': !equipment.is_available
              }" class="mr-1"></i>
              <div v-if="equipment.is_available" class="mr-1">
                {{ equipment.available_quantity }}
              </div>
              {{ equipment.is_available ? 'Available' : 'Unavailable' }}
            </span>

            <img v-if="equipment.images.length > 0" :src="`${equipment.images[0].image_url}`"
              :alt="equipment.images[0].image_url" class="w-full h-48 object-cover" />
            <img v-else src="https://via.placeholder.com/350" alt="Placeholder Image" class="w-full h-48 object-cover" />

            <span class="rating text-yellow-500">{{ renderStars(equipment.rating) }}</span>
            <span class="reviews text-gray-600">
              ({{ equipment.equipment_reviews ? equipment.equipment_reviews.length : 0 }} Reviews)
            </span>
          </div>

          <div class="p-1">
            <h5 class="text-sm font-semibold">
              {{ store.truncateText(equipment.name, 20) }}
            </h5>
            <p class="text-gray-600">{{ equipment.hourly_rate }} / Day</p>
          </div>
        </div>
      </div>
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

