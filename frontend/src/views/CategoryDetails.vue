<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router'; // Import useRoute to access query parameters
import axios from 'axios'; // Axios for API calls
import Hero from '@/components/Hero.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import Card from '@/components/Card.vue';
import EmptyList from '@/components/Empty.vue'; // Import the EmptyList component

import { useStore } from 'vuex';

const route = useRoute(); // Access the current route to get query parameters
const equipmentList = ref([]); // Store all equipment data
const filteredEquipments = ref([]); // Store filtered equipment based on category
const categoryMap = ref({}); // Store category slug to ID map

const search = useStore();


// Computed property to get searchQuery from Vuex
const searchQuery = computed(() => search.getters.getSearchQuery);

const api_base_url = import.meta.env.VITE_API_BASE_URL;



// Function to fetch category data and map slugs to IDs
const fetchCategories = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/categories/`); // Fetch categories from the API
    response.data.forEach(category => {
      categoryMap.value[category.slug] = category.id; // Create a mapping of slug to ID
    });
  } catch (error) {
    console.error('Error fetching category data:', error); // Log any error
  }
};

// Function to fetch equipment data from the API
const fetchEquipments = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/equipments/`); // Fetch equipment from the API
    equipmentList.value = response.data; // Store the fetched equipment data
    filterEquipments(); // Call the filter function once data is fetched
  } catch (error) {
    console.error('Error fetching equipment data:', error); // Log any error
  }
};

const filterEquipments = () => {
  const categorySlug = route.query.cat; // Get the 'cat' query parameter from the URL

  // Get the corresponding category ID from the slug
  const categoryId = categoryMap.value[categorySlug];
  if (!categoryId) {
    console.error('No matching category ID found for slug:', categorySlug);
    return; // Exit if there's no matching category ID
  }

  // Filter equipment based on the category ID and search query
  filteredEquipments.value = equipmentList.value.filter(equipment => {
    const matchesCategory = equipment.category === categoryId; // Match the category ID with the equipment category

    // Apply search query filtering if a search query exists
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      const matchesSearch = (
        equipment.name.toLowerCase().includes(query) ||
        equipment.description.toLowerCase().includes(query) ||
        equipment.hourly_rate.toString().includes(query) ||
        (equipment.address.street_address && equipment.address.street_address.toLowerCase().includes(query)) ||
        (equipment.address.city && equipment.address.city.toLowerCase().includes(query)) ||
        (equipment.address.state && equipment.address.state.toLowerCase().includes(query))
      );
      return matchesCategory && matchesSearch; // Return only if both category and search match
    }

    return matchesCategory; // Return only category match if no search query
  });

};


// Fetch data when the component mounts
onMounted(async () => {
  await fetchCategories(); // Fetch category data before fetching equipment
  await fetchEquipments(); // Fetch equipment data from the API after fetching categories

  // Watch for changes in searchQuery and refilter the equipment list
  watch(searchQuery, () => {
    filterEquipments();
  });
});
</script>

<template>
  <Hero />
  <Breadcrumb />

  <!-- Check if the equipment list is empty -->
  <EmptyList v-if="filteredEquipments.length === 0" />


  <!-- Render equipment for larger screens -->
  <div class="p-2 w-full hidden md:block" v-if="filteredEquipments.length > 0">
    <Card :equipments="filteredEquipments" />
  </div>

  <!-- Render equipment for smaller screens -->
  <div class="p-2 w-full text-xs md:hidden" v-if="filteredEquipments.length > 0">
    <Card :equipments="filteredEquipments" />
  </div>
</template>

<style scoped>
/* Additional styles can go here if needed */
</style>
