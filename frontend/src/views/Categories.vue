<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useStore } from 'vuex';
import Hero from '@/components/Hero.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import Filter from '@/components/Filter.vue';
import Card from '@/components/Card.vue';
import MobileFilter from '@/components/MobileFilter.vue';

// State to hold equipment and category data
const equipments = ref([]);
const categories = ref([]);
const cities = ref([]);
const selectedCategories = ref({});
const selectedCities = ref({});
const store = useStore();

// Computed property to get searchQuery from Vuex
const searchQuery = computed(() => store.getters.getSearchQuery);
const api_base_url = import.meta.env.VITE_API_BASE_URL;

// Fetch equipment and category data
onMounted(async () => {
  try {
    const equipmentResponse = await axios.get(`${api_base_url}/api/equipments/`);
    equipments.value = equipmentResponse.data;

    const categoryResponse = await axios.get(`${api_base_url}/api/categories`);
    categories.value = categoryResponse.data;

    // Initialize selected categories
    categories.value.forEach(category => {
      selectedCategories.value[category.name] = false;
    });

    // Extract cities from the equipment data (assuming each equipment has a city/location field)
    const equipmentCities = equipments.value.map(equipment => equipment.address?.city).filter(city => city);
    cities.value = [...new Set(equipmentCities)]; // Remove duplicates

  } catch (error) {
    console.error('Error fetching data:', error);
  }
});

// Create a map from category names to their IDs
const categoryIdMap = computed(() => {
  const map = {};
  categories.value.forEach(category => {
    map[category.name] = category.id;
  });
  return map;
});

// Computed property to filter equipments based on the search query and selected filters
const filteredEquipments = computed(() => {
  let filtered = equipments.value;

  // Apply search query filtering
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(equipment => {
      return (
        equipment.name.toLowerCase().includes(query) ||
        equipment.description.toLowerCase().includes(query) ||
        equipment.hourly_rate.toString().includes(query) ||
        (equipment.address.street_address && equipment.address.street_address.toLowerCase().includes(query)) ||
        (equipment.address.city && equipment.address.city.toLowerCase().includes(query)) ||
        (equipment.address.state && equipment.address.state.toLowerCase().includes(query))
      );
    });
  }

  // Apply category filtering
  const selectedCategoryKeys = Object.keys(selectedCategories.value).filter(key => selectedCategories.value[key]);

  if (selectedCategoryKeys.length > 0) {
    filtered = filtered.filter(equipment => {
      const equipmentCategoryId = equipment.category; // This is the ID
      const selectedCategoryIds = selectedCategoryKeys.map(name => categoryIdMap.value[name]); // Map names to IDs
      const match = selectedCategoryIds.includes(equipmentCategoryId);
      return match;
    });
  }

  // Apply city filtering
  const selectedCityKeys = Object.keys(selectedCities.value).filter(key => selectedCities.value[key]);

  if (selectedCityKeys.length > 0) {
    filtered = filtered.filter(equipment => {
      const match = selectedCityKeys.includes(equipment.address.city);
      return match;
    });
  }

  // Log the number of filtered equipments
  return filtered;
});
</script>

<template>
  <Hero />
  <Breadcrumb />

  <div class="container mx-auto py-4 w-5/6 hidden md:block">
    <div class="grid grid-cols-12 gap-4 p-1">
      <!-- Sidebar Section -->
      <aside class="col-span-3 bg-gray-100 rounded p-2">
        <Filter 
          :categories="categories" 
          :cities="cities" 
          :selectedCategories="selectedCategories" 
          :selectedCities="selectedCities" 
        />
      </aside>

      <!-- Main Content Section -->
      <main class="col-span-9 bg-gray-100 p-1">
        <Card :equipments="filteredEquipments" /> <!-- Pass filtered equipments -->
      </main>
    </div>
  </div>

  <div class="p-2 w-full text-xs md:hidden">
    <MobileFilter :categories="selectedCategories" />
    <Card :equipments="filteredEquipments" /> <!-- Pass filtered equipments -->
  </div>
</template>
