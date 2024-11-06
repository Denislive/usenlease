<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router'; // Import useRoute to access query parameters
import axios from 'axios'; // Axios for API calls
import Hero from '@/components/Hero.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import Card from '@/components/Card.vue';

const route = useRoute(); // Access the current route to get query parameters
const equipmentList = ref([]); // Store all equipment data
const filteredEquipments = ref([]); // Store filtered equipment based on category
const categoryMap = ref({}); // Store category slug to ID map

// Function to fetch category data and map slugs to IDs
const fetchCategories = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/categories/'); // Fetch categories from the API
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
    const response = await axios.get('http://127.0.0.1:8000/api/equipments/'); // Fetch equipment from the API
    equipmentList.value = response.data; // Store the fetched equipment data
    filterEquipments(); // Call the filter function once data is fetched
  } catch (error) {
    console.error('Error fetching equipment data:', error); // Log any error
  }
};

// Function to filter equipment based on the 'cat' query parameter from the URL
const filterEquipments = () => {
  const categorySlug = route.query.cat; // Get the 'cat' query parameter from the URL
  console.log(`Filtering equipment for category slug: ${categorySlug}`); // Debug log

  // Get the corresponding category ID from the slug
  const categoryId = categoryMap.value[categorySlug]; 
  if (!categoryId) {
    console.error('No matching category ID found for slug:', categorySlug);
    return; // Exit if there's no matching category ID
  }

  // Filter equipment based on the category ID
  filteredEquipments.value = equipmentList.value.filter(equipment => {
    const matches = equipment.category === categoryId; // Match the category ID with the equipment category
    console.log(`Checking equipment: ${equipment.name} (Category ID: ${equipment.category}) - Match: ${matches}`); // Log matching process
    return matches; // Return only equipment that matches the category ID
  });

  console.log('Filtered Equipments: ', filteredEquipments.value); // Debug log filtered results
};

// Fetch data when the component mounts
onMounted(async () => {
  await fetchCategories(); // Fetch category data before fetching equipment
  await fetchEquipments(); // Fetch equipment data from the API after fetching categories
});
</script>


<template>
  <Hero />
  <Breadcrumb />

  <!-- Render equipment for larger screens -->
  <div class="p-2 w-full hidden md:block">
    <Card :equipments="filteredEquipments" />
  </div>

  <!-- Render equipment for smaller screens -->
  <div class="p-2 w-full text-xs md:hidden">
    <Card :equipments="filteredEquipments" />
  </div>
</template>
