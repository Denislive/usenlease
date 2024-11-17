<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments'; // Import your Pinia store
import { useStore } from 'vuex';

const router = useRouter();
const store = useEquipmentsStore(); // Create an instance of the equipments store
const search = useStore();


// Computed property to get searchQuery from Vuex
const searchQuery = computed(() => search.getters.getSearchQuery);




// Fetch equipments and categories when the component is mounted
onMounted(async () => {
  await store.fetchEquipments(); // Fetch equipments
  await store.fetchCategories(); // Fetch categories
});

// Use the fetched equipments from the store
const equipments = computed(() => store.equipments);
const categories = computed(() => store.categories);


// Computed property for filtered equipments
const filteredEquipments = computed(() => {
  if (!searchQuery.value) return equipments.value; // Return all if no search query

  const query = searchQuery.value.toLowerCase(); // Convert search query to lower case for case insensitive matching

  return equipments.value.filter(equipment => {
    // Check if the search query is found in any of the specified fields
    return (
      equipment.name.toLowerCase().includes(query) ||
      equipment.description.toLowerCase().includes(query) ||
      equipment.hourly_rate.toString().includes(query) || // Ensure hourly_rate is a string
      (equipment.address.street_address && equipment.address.street_address.toLowerCase().includes(query)) ||
      (equipment.address.city && equipment.address.city.toLowerCase().includes(query)) ||
      (equipment.address.state && equipment.address.state.toLowerCase().includes(query))
    );
  });
});

const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  } else {
    console.error('Equipment ID is missing!'); // Log an error if ID is missing
  }
}
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
            :src="`http://127.0.0.1:8000${equipment.images[0].image_url}`"
            :alt="equipment.images[0].image_url"
            class="w-full h-48 object-cover"
          />
          <img
            v-else
            src="https://via.placeholder.com/350"
            alt="Placeholder Image"
            class="w-full h-48 object-cover"
          />

          <!-- Add to Cart Button -->
          <a
            href="#"
            class="absolute bottom-4 right-4 bg-[#1c1c1c] text-white rounded-full h-10 w-10 flex items-center justify-center hover:text-[#ffc107] transition"
          >
            <i class="pi pi-cart-arrow-down"></i>
          </a>
        </div>

        <!-- Equipment Details -->
        <div class="p-4">
          <h5 class="text-lg font-semibold">{{ equipment.name }}</h5>
          <p class="text-gray-600">{{ equipment.hourly_rate }} / Hr</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Optional additional styles can go here */
</style>
