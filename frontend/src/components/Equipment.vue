<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments'; // Pinia store for equipments
import { useStore } from 'vuex';

const router = useRouter();

const api_base_url = import.meta.env.VITE_API_BASE_URL;

const store = useEquipmentsStore(); // Pinia store instance
const search = useStore();

// Computed property to get searchQuery from Vuex
const searchQuery = computed(() => search.getters.getSearchQuery);

// Fetch equipments and categories when the component is mounted
onMounted(async () => {
  await store.fetchEquipments(); // Fetch equipments
  await store.fetchCategories(); // Fetch categories
});

// Computed property for equipments and categories
const equipments = computed(() => store.equipments);
const categories = computed(() => store.categories);

// Computed property for filtered equipments
const filteredEquipments = computed(() => {
  if (!searchQuery.value) return equipments.value; // Return all if no search query

  const query = searchQuery.value.toLowerCase(); // Case-insensitive matching

  return equipments.value.filter(equipment => {
    // Check if the search query matches any of the specified fields
    return (
      equipment.name.toLowerCase().includes(query) ||
      equipment.description.toLowerCase().includes(query) ||
      equipment.hourly_rate.toString().includes(query) || // Ensure hourly_rate is a string
      (equipment.address?.street_address?.toLowerCase().includes(query)) ||
      (equipment.address?.city?.toLowerCase().includes(query)) ||
      (equipment.address?.state?.toLowerCase().includes(query))
    );
  });
});

// Function to navigate to equipment details page
const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  } else {
    console.error('Equipment ID is missing!');
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
  <div class="container mx-auto p-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <!-- Loop through the filtered equipments -->
      <div
        v-for="equipment in filteredEquipments"
        :key="equipment.id"
        @click="() => { goToDetail(equipment.id) }"
        class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer"
      >
        <div class="relative">
          <!-- Availability Badge -->
          <span
            :class="{
              'bg-green-500': equipment.is_available,
              'bg-red-500': !equipment.is_available
            }"
            class="absolute top-2 left-2 text-white text-xs font-bold px-2 py-1 rounded flex items-center"
          >
            <i
              :class="{
                'pi pi-check-circle': equipment.is_available,
                'pi pi-times-circle': !equipment.is_available
              }"
              class="mr-1"
            ></i>
            {{ equipment.is_available ? 'Available' : 'Unavailable' }}
          </span>

          <!-- Equipment Image -->
          <img
            v-if="equipment.images.length > 0"
            :src="`${api_base_url}${equipment.images[0].image_url}`"
            :alt="equipment.images[0].image_url"
            class="w-full h-48 object-cover"
          />
          <img
            v-else
            src="https://via.placeholder.com/350"
            alt="Placeholder Image"
            class="w-full h-48 object-cover"
          />

          <!-- reviews and rating -->
          <span class="rating text-yellow-500">{{ renderStars(equipment.rating) }}</span>
          <span class="reviews text-gray-600"> ({{ equipment.equipment_reviews ? equipment.equipment_reviews.length : 0 }} Reviews)</span>
        </div>

        <!-- Equipment Details -->
        <div class="p-4">
          <h5 class="text-sm font-semibold">{{ equipment.name }}</h5>
          <p class="text-gray-600">{{ equipment.hourly_rate }} / Hr</p>
        </div>
      </div>
    </div>

    <!-- Empty State Message -->
    <div class="empty-list-container text-center py-16" v-if="filteredEquipments.length === 0">
      <i class="pi pi-exclamation-circle text-9xl text-gray-500"></i>
      <p class="text-xl text-gray-500 mt-4">Oops! No items in here!</p>
      <p class="text-xl text-gray-500 mt-4">Try adding a new item by hitting the lease button.</p>
    </div>
  </div>
</template>

<style scoped>
/* Optional additional styles can go here */
</style>
