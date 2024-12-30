<template>
  <!-- Categories Section for Mobile -->
  <section class="mobile-categories py-3 block md:hidden">
    <div class="container mx-auto">
      <div class="grid grid-cols-3 gap-4">
        <!-- Post Ad Button (CTA Component) -->
        <div class="col-span-1">
          <RouterLink
            class="flex flex-col items-center justify-center h-28 bg-[#1c1c1c] text-white rounded-lg shadow-lg hover:text-[#ffc107] transition duration-300"
            to="/list-item">
            <i class="pi pi-plus text-3xl mb-2"></i>
            <span class="main-text text-sm font-semibold text-center">equipment</span>
          </RouterLink>
        </div>

        <!-- Dynamic Category Cards -->
        <div v-for="category in store.categories" :key="category.id">
          <div class="bg-white rounded-lg shadow-lg overflow-hidden">
            <RouterLink :to="{ name: 'category-details', query: { cat: category.slug } }">
              <img :src="category.image ? `${category.image}` || placeholderImage
                : alt = `${category.name}`" class="w-full h-12 object-cover" />
              <div class="p-1 text-center">
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
import { useEquipmentsStore } from '@/store/equipments'; // Pinia store for equipments


const api_base_url = import.meta.env.VITE_API_BASE_URL;
const store = useEquipmentsStore(); // Pinia store instance



// Placeholder image in case category image is null
const placeholderImage = 'https://via.placeholder.com/300x200.png?text=No+Image';



// Fetch categories when the component mounts
onMounted(async () => {
  await store.fetchCategories();
});
</script>

<style scoped>
/* Additional styles can go here if needed */
</style>