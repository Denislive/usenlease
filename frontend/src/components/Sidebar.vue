<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const categories = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchCategories = async () => {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/root-categories/`);
    categories.value = response.data;
  } catch (err) {
    error.value = 'Failed to fetch categories. Please try again later.';
  } finally {
    loading.value = false;
  }
};

// Fetch categories when the component mounts
onMounted(() => {
  fetchCategories();
});

// Computed property to determine the ad count
const getAdCount = (category) => {
  if (!category.subcategories || category.subcategories.length === 0) {
    return category.ad_count || 0; // Parent category ad count
  }
  return category.subcategories.reduce((count, sub) => count + sub.ad_count, 0); // Sum of subcategories' ad counts
};
</script>

<template>
  <div class="sidebar-content">
    <template v-if="loading">
      <p>Loading categories...</p>
    </template>
    <template v-else-if="error">
      <p class="text-red-600">{{ error }}</p>
    </template>
    <template v-else>
      <ul class="categories-list list-none p-0 m-0 space-y-2">
        <li
          v-for="category in categories"
          :key="category.id"
          class="category-item relative group"
        >
          <RouterLink
            :to="{ name: 'category-details', query: { cat: category.slug } }"
            class="flex items-center p-1 bg-white rounded-lg transition-shadow duration-300 text-gray-800 shadow hover:bg-yellow-100 hover:shadow-lg"
          >
            <img
              :src="category.image ? category.image : 'Category image'"
              :alt="category.name"
              class="category-icon w-8 h-6 object-cover rounded border-2 border-yellow-400 mr-2"
            >
            <div class="category-name-container">
              <span class="category-name font-semibold text-sm">{{ category.name }}</span>
              <span class="ad-count text-xs text-gray-500">
                ({{ getAdCount(category) }})
              </span>
            </div>
          </RouterLink>
          <ul class="subcategories-list list-none pl-4 mt-1 hidden group-hover:block">
            <li
              v-for="subcategory in category.subcategories"
              :key="subcategory.id"
              class="subcategory-item"
            >
              <RouterLink
                :to="{ name: 'category-details', query: { cat: subcategory.slug } }"
                class="flex items-center p-1 bg-white rounded-lg transition-colors duration-300 text-gray-800 hover:bg-yellow-100 transform hover:translate-x-1"
              >
                <img
                  :src="subcategory.image ? subcategory.image : 'SubCategory Image'"
                  :alt="subcategory.name"
                  class="subcategory-icon w-8 h-6 object-cover rounded border-2 border-yellow-400 mr-2"
                >
                <div class="subcategory-name-container flex-1">
                  <span class="subcategory-name font-medium text-sm">{{ subcategory.name }}</span>
                  <span class="ad-count text-xs text-gray-400"> ({{ subcategory.ad_count }})</span>
                </div>
              </RouterLink>
            </li>
          </ul>
        </li>
      </ul>
    </template>
  </div>
</template>
