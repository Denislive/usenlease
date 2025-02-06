<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';
import { useStore } from 'vuex';

const router = useRouter();
const api_base_url = import.meta.env.VITE_API_BASE_URL;

const store = useEquipmentsStore();
const search = useStore();

const searchQuery = computed(() => search.getters.getSearchQuery);

const itemsPerPage = 20; // Items per page
const currentPage = ref(1); // Current page number

onMounted(async () => {
  await store.fetchEquipments();
  await store.fetchCategories();
});

const equipments = computed(() => store.equipments);
const categories = computed(() => store.categories);


const filteredEquipments = computed(() => {
  if (!searchQuery.value) return equipments.value;

  const query = searchQuery.value.toLowerCase();

  return equipments.value.filter((equipment) => {
    return (
      equipment.name.toLowerCase().includes(query) ||
      equipment.description.toLowerCase().includes(query) ||
      equipment.hourly_rate.toString().includes(query) ||
      (equipment.address?.street_address?.toLowerCase().includes(query)) ||
      (equipment.address?.city?.toLowerCase().includes(query)) ||
      (equipment.address?.state?.toLowerCase().includes(query))
    );
  });
});

// Paginated Equipments
const paginatedEquipments = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return filteredEquipments.value.slice(startIndex, endIndex);
});

// Total Pages
const totalPages = computed(() =>
  Math.ceil(filteredEquipments.value.length / itemsPerPage)
);

// Navigate to a specific page
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  } else {
    showNotification('Item Error', 'Equipment ID is missing!', 'error');
  }
};

const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  const emptyStars = 5 - fullStars - halfStar;

  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(emptyStars);
};
</script>

<template>
  <div class="container mx-auto p-2">
    <!-- Equipment List Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 auto-rows-auto">
      <div 
        v-for="equipment in paginatedEquipments" 
        :key="equipment.id" 
        @click="goToDetail(equipment.id)"
        class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer flex flex-col">
        
        <!-- Equipment Status -->
        <div class="relative p-1">
          <span v-if="equipment.is_available" 
            class="absolute top-2 left-2 text-white text-xs font-semibold px-3 py-1 rounded-full flex items-center"
            :class="equipment.is_available ? 'bg-green-500' : 'bg-red-500'">
            <i class="pi pi-check-circle mr-1"></i>
            {{ equipment.available_quantity }} Available
          </span>
          <span v-else class="text-red-500 text-xs font-semibold">Temporarily Unavailable</span>
        </div>

        <!-- Availability Dates -->
        <div v-if="equipment.booked_dates_data?.length" class="text-xs text-blue-600 px-2" :class="equipment.is_available ? 'mt-6' : 'mt-0'">
          <ul class="pl-0">
            <li v-for="(date, index) in equipment.booked_dates_data" :key="index" class="">
              <span>{{ equipment.available_quantity + date.quantity }} available between: </span>
              <span class="text-black">{{ date.start_date }} - {{ date.end_date }}</span>
            </li>
          </ul>
        </div>

        <!-- Equipment Image -->
        <img 
          :src="equipment.images.length ? equipment.images[0].image_url : 'https://via.placeholder.com/350'" 
          :alt="equipment.images.length ? equipment.name : 'Placeholder Image'" 
          class="w-full h-48 object-cover rounded-t-lg mt-4 flex-grow" 
        />

        <!-- Equipment Information -->
        <div class="p-4 border-t flex flex-col">
          <h5 class="text-sm font-semibold mb-1 text-gray-900">
            {{ store.truncateText(equipment.name, 20) }}
          </h5>
          <p class="text-gray-600 mb-2">${{ equipment.hourly_rate }} / Day</p>

          <!-- Rating and Reviews -->
          <div class="flex items-center mb-2">
            <span class="rating text-yellow-500 mr-1">{{ renderStars(equipment.rating) }}</span>
            <span class="reviews text-gray-600 text-xs">
              ({{ equipment.equipment_reviews?.length || 0 }} Reviews)
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty List Message -->
    <div v-if="filteredEquipments.length === 0" class="text-center py-16">
      <i class="pi pi-exclamation-circle text-9xl text-gray-500"></i>
      <p class="text-xl text-gray-500 mt-4">Oops! No items here!</p>
      <p class="text-xl text-gray-500 mt-4">Try adding a new item by hitting the lease button.</p>
    </div>

    <!-- Pagination Controls -->
    <div v-if="totalPages > 1" class="pagination flex justify-center mt-6">
      <button 
        :disabled="currentPage === 1" 
        @click="goToPage(currentPage - 1)"
        class="px-4 py-2 mx-1 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50">
        Previous
      </button>

      <button 
        v-for="page in totalPages" :key="page" @click="goToPage(page)"
        class="px-4 py-2 mx-1 rounded-lg"
        :class="page === currentPage ? 'bg-black text-white' : 'bg-yellow-500 hover:bg-gray-300'">
        {{ page }}
      </button>

      <button 
        :disabled="currentPage === totalPages" 
        @click="goToPage(currentPage + 1)"
        class="px-4 py-2 mx-1 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50">
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Optional styles for pagination */
</style>
