<template>
  <section class="hero bg-gradient-to-r from-[#ff9e00] to-[#ffc107] py-1 px-1 relative text-white overflow-hidden flex items-center">
    <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-50"></div>

    <div class="container mx-auto flex flex-col lg:flex-row items-center justify-between relative z-10 w-full">
      <!-- Left Section: Heading Only -->
      <div class="text-left lg:w-1/3">
        <h1 class="text-2xl lg:text-3xl font-bold leading-tight animate__animated animate__fadeIn">
          Rent the Best Equipment
        </h1>
      </div>

      <!-- Right Section: Paragraph & Search -->
      <div class="lg:w-2/3 flex flex-col gap-2 lg:flex-row items-center lg:justify-end mt-1 lg:mt-0">
        <!-- Paragraph -->
        <p class="text-sm text-white/90 text-center lg:text-left animate__animated animate__fadeIn animate__delay-1s">
          Find high-quality equipment for any project. Fast delivery and excellent support.
        </p>

        <!-- Search Box -->
        <div class="w-full max-w-lg bg-white p-2 rounded shadow-xl flex items-center space-x-1 transition-all">
          <!-- Category Select -->
          <select
            v-model="selectedCategory"
            @change="fetchEquipmentsData"
            class="w-24 bg-white text-[#1c1c1c] text-sm p-2 border-r border-gray-300 focus:outline-none cursor-pointer rounded-l-full"
          >
            <option value="All">All</option>
            <option v-for="category in categories" :key="category.id" :value="category.slug">
              {{ category.name }}
            </option>
          </select>

          <!-- Search Input -->
          <input
            type="text"
            v-model="searchQuery"
            @input="debouncedSearch"
            class="flex-1 text-[#1c1c1c] border-none text-sm focus:outline-none px-3 py-2"
            placeholder="I am looking for..."
          />

          <!-- Search Button -->
          <button
            @click="fetchEquipmentsData"
            class="bg-[#ff6f00] text-white px-4 py-2 rounded-full transition duration-300 hover:bg-[#ff9e00] transform hover:scale-105 flex items-center justify-center"
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
import { useEquipmentsStore } from '@/store/equipments';
import { debounce } from 'lodash';

const store = useEquipmentsStore();

const searchQuery = ref('');
const selectedCategory = ref('All');

// Fetch categories and equipments on mount
onMounted(() => {
  store.fetchCategories();
  fetchEquipmentsData();
});

// Computed property for categories
const categories = computed(() => store.categories);

// Function to fetch equipment based on filters
const fetchEquipmentsData = async () => {
  const filters = {
    category: selectedCategory.value === 'All' ? '' : selectedCategory.value,
    search: searchQuery.value
  };

  if (!filters.search && !filters.category) {
    // No filters, fetch all
    await store.fetchEquipments();
  } else {
    // Apply filters
    await store.fetchFilteredEquipments(filters);
  }
};

// Debounced search to avoid unnecessary API calls
const debouncedSearch = debounce(fetchEquipmentsData, 700);
</script>
