<template>
  <!-- Categories Section for Mobile -->
  <section class="mobile-categories py-3 block md:hidden">
    <div class="container mx-auto">
      <div class="grid grid-cols-3 gap-4">
        <!-- Post Ad Button (CTA Component) -->
        <div class="col-span-1">
          <RouterLink
            class="flex flex-col items-center justify-center h-48 bg-[#1c1c1c] text-white rounded-lg shadow-lg hover:text-[#ffc107] transition duration-300"
            to="/list-item">
            <i class="pi pi-plus text-3xl mb-2"></i>
            <span class="main-text text-sm font-semibold text-center">equipment</span>
          </RouterLink>
        </div>

        <!-- Dynamic Category Cards -->
        <div v-for="category in categories" :key="category.id">
          <div class="bg-white rounded-lg shadow-lg overflow-hidden">
            <RouterLink :to="{ name: 'category-details', query: { cat: category.slug } }">
              <img :src="category.image ? `${api_base_url}${category.image}` || placeholderImage
                : alt = `${category.name}`" class="w-full h-32 object-cover" />
              <div class="p-4 text-center">
                <h5 class="text-sm">{{ category.name }}</h5>
              </div>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </section>
  <Carousels />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Carousels from "./Carousels.vue";


const api_base_url = import.meta.env.VITE_API_BASE_URL;

// Placeholder image in case category image is null
const placeholderImage = 'https://via.placeholder.com/300x200.png?text=No+Image';

// Dynamic categories data
const categories = ref([]);

// Function to fetch categories from the API
const fetchCategories = async () => {
  try {
    const response = await fetch(`${api_base_url}/api/categories/`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    categories.value = data; // Assuming data is an array of categories
  } catch (error) {
    console.error('Error fetching categories:', error);
  }
};

// Fetch categories when the component mounts
onMounted(() => {
  fetchCategories();
});
</script>

<style scoped>
/* Additional styles can go here if needed */
</style>