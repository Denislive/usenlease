<script setup>
import { ref, onMounted, computed } from 'vue';
import { useEquipmentsStore } from '@/store/equipments'; // Import the equipments store
import { RouterLink } from 'vue-router'; // Import RouterLink
import axios from 'axios';
const store = useEquipmentsStore(); // Create an instance of the equipments store

// Reactive properties for loading and error states
const loading = computed(() => store.isLoading); // Loading state from the store
const error = computed(() => store.error); // Error state from the store

const categories = ref([]);

const fetchCategories = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/root-categories/');
    categories.value = response.data;
  } catch (err) {
    console.error('Error fetching root categories:', err);
    error.value = 'Failed to fetch categories. Please try again later.';
  } finally {
    loading.value = false; // Reset loading state once the request is done
  }
};

// Fetch categories when the component mounts
onMounted(() => {
    fetchCategories(); // Use the store method to fetch categories
});
</script>

<template>
    <aside class="cell medium-4 large-3 categories-sidebar">
        <div class="sidebar-content">
            <template v-if="loading">
                <p>Loading categories...</p> <!-- Loading message -->
            </template>
            <template v-else-if="error">
                <p class="text-red-600">{{ error }}</p> <!-- Error message -->
            </template>
            <template v-else>
                <ul class="categories-list list-none p-0 m-0 space-y-5">
                    <li v-for="category in categories" :key="category.id" class="category-item relative mb-5 group">
                        <RouterLink
                            :to="{ name: 'category-details', query: { cat: category.slug } }"
                            class="flex items-center p-2 bg-white rounded-lg transition-shadow duration-300 text-gray-800 shadow hover:bg-yellow-100 hover:shadow-lg"
                        >
                            <img :src="category.image ? category.image : 'https://picsum.photos/100/150'" 
                            :alt="category.name" 
                                 class="category-icon w-12 h-12 object-cover rounded-full border-2 border-yellow-400 mr-3">
                            <div class="category-name-container">
                                <span class="category-name font-semibold">{{ category.name }}</span>
                                <span class="ad-count text-gray-500">
                                    ({{ category.subcategories ? category.subcategories.reduce((count, sub) => count + sub.ad_count, 0) : 0 }})
                                </span>
                            </div>
                        </RouterLink>
                        <ul class="subcategories-list list-none p-0 mt-2 hidden group-hover:block left-0 z-10" style="top: calc(100% + 0.5rem); left: 0; width: 100%;">
                            <li v-for="subcategory in category.subcategories" :key="subcategory.id" class="subcategory-item mb-2">
                                <RouterLink 
                                    :to="{ name: 'category-details', query: { cat: category.slug, sub: subcategory.slug } }" 
                                    class="flex items-center p-2 bg-white rounded-lg transition-colors duration-300 text-gray-800 hover:bg-yellow-100 transform hover:translate-x-1">
                                    <img :src="subcategory.image ? subcategory.image : 'https://picsum.photos/100/150'" 
                                         :alt="subcategory.name" 
                                         class="subcategory-icon w-9 h-9 object-cover rounded-full border-2 border-yellow-400 mr-2">
                                    <div class="subcategory-name-container flex-1">
                                        <span class="subcategory-name font-medium">{{ subcategory.name }}</span>
                                        <span class="ad-count text-xs text-gray-400">({{ subcategory.ad_count }})</span>
                                    </div>
                                </RouterLink>
                            </li>
                        </ul>
                    </li>
                </ul>
            </template>
        </div>
    </aside>
</template>

<style scoped>
/* Custom Scrollbar for Sidebar */
.categories-sidebar::-webkit-scrollbar {
    width: 8px;
}

.categories-sidebar::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.categories-sidebar::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 10px;
}

.categories-sidebar::-webkit-scrollbar-thumb:hover {
    background: #999;
}

/* Custom styles for subcategories */
.subcategory-item {
    opacity: 0; /* Start with hidden subcategories */
    transition: opacity 0.3s ease; /* Smooth transition */
    margin-left: 2rem; /* Indentation with left margin */
}

.category-item:hover .subcategory-item {
    opacity: 1; /* Fade in on hover */
}
</style>
