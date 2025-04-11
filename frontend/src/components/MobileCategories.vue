<template>
  <!-- Mobile Categories Section -->
  <section class="mobile-categories py-3 block md:hidden" aria-label="Item categories">
    <div class="container mx-auto px-4">
      <div class="grid grid-cols-3 gap-4">
        <!-- Post Ad Button (CTA) -->
        <div class="col-span-1">
          <RouterLink
            to="/list-item"
            class="flex flex-col items-center justify-center h-28 bg-[#1c1c1c] text-white rounded-lg shadow-lg hover:text-[#ffc107] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-[#ffc107]"
            aria-label="Post new item"
          >
            <i class="pi pi-plus text-3xl mb-2" aria-hidden="true"></i>
            <span class="text-sm font-semibold text-center">Post Item</span>
          </RouterLink>
        </div>

        <!-- Dynamic Category Cards -->
        <template v-for="category in store.categories" :key="`mobile-cat-${category.id}`">
          <div class="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
            <RouterLink 
              :to="{ name: 'category-details', query: { cat: category.slug } }" 
              class="block h-full"
              :aria-label="`Browse ${category.name} Items`"
            >
              <div class="h-12 bg-gray-100 flex items-center justify-center">
                <img 
                  v-if="category.image"
                  :src="getImageUrl(category.image)" 
                  :alt="`${category.name} category`"
                  class="w-full h-full object-cover"
                  loading="lazy"
                  width="100"
                  height="48"
                  @error="handleImageError"
                />
                <div v-else class="flex items-center justify-center w-full h-full bg-gray-200">
                  <i class="pi pi-image text-2xl text-gray-500" aria-hidden="true"></i>
                </div>
              </div>
              <div class="p-2 text-center">
                <h5 class="text-sm font-medium text-gray-800 truncate px-1">{{ category.name }}</h5>
              </div>
            </RouterLink>
          </div>
        </template>
      </div>
    </div>
  </section>

  <Carousels />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Carousels from "./Carousels.vue";
import { useEquipmentsStore } from '@/store/equipments';

// Constants
const DEFAULT_CATEGORY_ICON = 'pi-image';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Store
const store = useEquipmentsStore();

/**
 * Generates proper image URL
 * @param {string} imagePath - Image path from API
 * @returns {string} Full image URL
 */
const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  if (imagePath.startsWith('http')) return imagePath;
  return `${API_BASE_URL}${imagePath.startsWith('/') ? '' : '/'}${imagePath}`;
};

/**
 * Handles image loading errors
 * @param {Event} event - Error event
 */
const handleImageError = (event) => {
  // Replace the image element with icon container
  const parent = event.target.parentElement;
  parent.innerHTML = `
    <div class="flex items-center justify-center w-full h-full bg-gray-200">
      <i class="pi ${DEFAULT_CATEGORY_ICON} text-2xl text-gray-500" aria-hidden="true"></i>
    </div>
  `;
};

// Fetch categories when component mounts
onMounted(async () => {
  try {
    await store.fetchCategories();
  } catch (error) {
    console.error('Failed to fetch categories:', error);
  }
});
</script>

<style scoped>
.mobile-categories {
  min-height: 200px;
}

/* Focus styles for accessibility */
a:focus {
  outline: 2px solid #ffc107;
  outline-offset: 2px;
}

/* Smooth transitions for interactive elements */
.router-link-active {
  @apply ring-2 ring-[#ffc107];
}
</style>