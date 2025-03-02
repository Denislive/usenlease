<template>
  <section class="hero bg-gradient-to-r from-[#ff9e00] to-[#ffc107] py-2 lg:py-1 relative text-white overflow-hidden flex items-center">
    <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-60"></div>

    <div class="container mx-auto text-center relative z-10 px-4">
      <h1 class="text-2xl lg:text-4xl font-bold leading-tight mb-4 animate__animated animate__fadeIn">
        Rent the Best Equipment for Your Needs
      </h1>
      <p class="text-xs text-black lg:text-lg mb-6 animate__animated animate__fadeIn animate__delay-1s">
        Find top-quality equipment for any project. Fast delivery and great customer support.
      </p>

      <div class="flex justify-center">
        <div class="w-full max-w-lg bg-white p-2 rounded-lg shadow-lg flex items-center">
          <!-- Category Select (Static Width) -->
          <select
            v-model="selectedCategory"
            @change="handleCategoryChange"
            class="w-28 bg-white text-[#1c1c1c] p-2 border-r border-gray-300 focus:outline-none cursor-pointer"
          >
            <!-- Conditionally render the "All" option -->
            <option value="All">All</option>
            
            <!-- Render categories from the store -->
            <option v-for="category in categories" :key="category.id" :value="category.slug">
              {{ category.name }}
            </option>
          </select>

          <!-- Search Input (Smaller Size) -->
          <input
            type="text"
            v-model="searchQuery"
            @input="debouncedSearch"
            class="flex-1 w-full text-[#1c1c1c] border-none text-sm lg:text-base focus:outline-none px-3 py-2"
            placeholder="I am looking for..."
          />

          <!-- Search Button -->
          <button
            @click="filterBySearch"
            class="bg-[#ff6f00] text-white px-4 py-2 rounded-md transition duration-300 hover:bg-[#ff9e00] transform hover:scale-105"
          >
            <i class="pi pi-search text-lg"></i>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';
import { debounce } from 'lodash';

const router = useRouter();
const store = useEquipmentsStore();

const searchQuery = ref('');
const selectedCategory = ref('All');

// Fetch categories and equipments on mount
onMounted(() => {
  store.fetchCategories();
  store.fetchEquipments();
});

// Computed property for categories
const categories = computed(() => store.categories);

// Handle category change
const handleCategoryChange = async () => {
  if (selectedCategory.value === 'All') {
    // Reset search query and fetch all equipments
    searchQuery.value = '';
    store.searchQuery = '';
    router.push('/'); // Navigate to the home page
    await store.fetchEquipments(); // Ensure equipment data is updated
    store.filteredEquipments = store.equipments;
  } else {
    // Filter based on the selected category
    router.push({ name: 'category-details', query: { cat: selectedCategory.value } });
  }
};

// Function to update search query
const filterBySearch = () => {
  store.searchQuery = searchQuery.value;
};

// Debounced search to avoid filtering on every keystroke
const debouncedSearch = debounce(filterBySearch, 700);
</script>