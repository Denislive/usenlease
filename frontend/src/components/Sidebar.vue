<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { RouterLink } from 'vue-router';

const categories = ref([]);
const loading = ref(true);
const error = ref(null);
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

const fetchCategories = async () => {
  try {
    loading.value = true;
    error.value = null;

    const response = await axios.get(`${apiBaseUrl}/api/root-categories/`, {
      withCredentials: true // Include credentials if needed
    });

    if (response.status !== 200) {
      throw new Error('Failed to fetch categories');
    }

    categories.value = response.data.map(category => ({
      ...category,
      // Ensure subcategories is always an array
      subcategories: Array.isArray(category.subcategories) ? category.subcategories : []
    }));

  } catch (err) {
    console.error('Error fetching categories:', err);
    error.value = err.response?.data?.message || 'Failed to fetch categories. Please try again later.';
  } finally {
    loading.value = false;
  }
};

// Computed property for total categories count
const totalCategories = computed(() => categories.value.length);

// Calculate ad count with proper fallbacks
const getAdCount = (category) => {
  if (!category) return 0;

  // If no subcategories, return the category's ad_count or 0
  if (!category.subcategories || category.subcategories.length === 0) {
    return Number(category.ad_count) || 0;
  }

  // Sum subcategories' ad counts safely
  return category.subcategories.reduce((count, sub) => {
    return count + (Number(sub.ad_count) || 0);
  }, 0);
};

// Fetch categories on mount with error handling
onMounted(async () => {
  try {
    await fetchCategories();
  } catch (err) {
    console.error('Component mount error:', err);
  }
});
</script>

<template>
  <aside class="sidebar-content" aria-label="Categories navigation">
    <!-- Loading State -->
    <div v-if="loading" class="p-4">
      <div class="flex items-center space-x-2">
        <div class="w-5 h-5 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin"></div>
        <span class="text-sm text-gray-600">Loading categories...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="p-4 bg-red-50 rounded-lg">
      <p class="text-red-600 text-sm flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
            clip-rule="evenodd" />
        </svg>
        {{ error }}
      </p>
      <button @click="fetchCategories" class="mt-2 text-xs text-blue-600 hover:text-blue-800 focus:outline-none">
        Retry
      </button>
    </div>

    <!-- Success State -->
    <template v-else>
      <div v-if="totalCategories > 0" class="categories-container">
        <h2 class="sr-only">Categories</h2>
        <ul class="categories-list space-y-2">
          <li v-for="category in categories" :key="`category-${category.id}`" class="category-item group">
            <RouterLink :to="{ name: 'category-details', query: { cat: category.slug } }" class="category-link"
              :aria-label="`Browse ${category.name} category (${getAdCount(category)} items)`">
              <div class="flex items-center">
                <!-- Category Image with Fallback -->
                <div class="image-container">
                  <img v-if="category.image" :src="category.image" :alt="category.name" class="category-image"
                    loading="lazy">
                  <div v-else class="w-full h-full bg-gray-100 flex items-center justify-center">
                    <i class="pi pi-image text-4xl text-gray-400"></i>
                  </div>
                </div>

                <div class="text-container">
                  <span class="category-name">{{ category.name }}</span>
                  <span class="ad-count">({{ getAdCount(category) }})</span>
                </div>
              </div>
            </RouterLink>

            <!-- Subcategories -->
            <transition name="fade">
              <ul v-if="category.subcategories.length > 0" class="subcategories-list" :aria-expanded="false">
                <li v-for="subcategory in category.subcategories" :key="`subcategory-${subcategory.id}`"
                  class="subcategory-item">
                  <RouterLink :to="{ name: 'category-details', query: { cat: subcategory.slug } }"
                    class="subcategory-link"
                    :aria-label="`Browse ${subcategory.name} subcategory (${subcategory.ad_count} items)`">
                    <div class="flex items-center">
                      <!-- Subcategory Image with Fallback -->
                      <div class="image-container">
                        <img v-if="subcategory.image" :src="subcategory.image" :alt="subcategory.name"
                          class="subcategory-image" loading="lazy">
                        <div v-else class="w-full h-full bg-gray-100 flex items-center justify-center">
                          <i class="pi pi-image text-4xl text-gray-400"></i>
                        </div>
                      </div>

                      <div class="text-container">
                        <span class="subcategory-name">{{ subcategory.name }}</span>
                        <span class="ad-count">({{ subcategory.ad_count || 0 }})</span>
                      </div>
                    </div>
                  </RouterLink>
                </li>
              </ul>
            </transition>
          </li>
        </ul>
      </div>

      <!-- Empty State -->
      <div v-else class="p-4 text-center text-gray-500 text-sm">
        No categories available
      </div>
    </template>
  </aside>
</template>

<style scoped>
.sidebar-content {
  @apply w-full;
}

.categories-list {
  @apply list-none p-0 m-0;
}

.category-item {
  @apply relative;
}

.category-link {
  @apply flex items-center p-2 bg-white rounded-lg transition-all duration-200 text-gray-800 hover:bg-yellow-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-yellow-400;
}

.subcategories-list {
  @apply list-none pl-6 mt-1 space-y-1 max-h-0 overflow-hidden transition-all duration-300 ease-in-out;
}

.group:hover .subcategories-list {
  @apply max-h-screen py-1;
}

.subcategory-link {
  @apply flex items-center p-2 bg-gray-50 rounded-lg transition-all duration-200 text-gray-700 hover:bg-yellow-100 hover:translate-x-1 focus:outline-none focus:ring-1 focus:ring-yellow-400;
}

.image-container {
  @apply flex-shrink-0;
}

.category-image,
.subcategory-image {
  @apply w-8 h-6 object-cover rounded border-2 border-yellow-400 mr-3;
}

.text-container {
  @apply flex items-baseline flex-1;
}

.category-name,
.subcategory-name {
  @apply font-medium text-sm truncate;
}

.ad-count {
  @apply text-xs text-gray-500 ml-1;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>