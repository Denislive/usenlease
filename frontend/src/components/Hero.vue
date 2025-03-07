<template>
  <section class="hero bg-gradient-to-r from-[#ff9e00] to-[#ffc107] py-1 px-1  relative text-white overflow-hidden flex items-center">
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
        <p class="text-sm text-white/90 text-center lg:text-left animate__animated animate__fadeIn animate__delay-1s">
          Find high-quality equipment for any project. Fast delivery and excellent support.
        </p>

        <!-- Search Box -->
        <div class="w-full max-w-lg bg-white p-2 rounded shadow-xl flex items-center space-x-1 transition-all">
          <select
            v-model="selectedCategory"
            @change="handleCategoryChange"
            class="w-24 bg-white text-[#1c1c1c] text-sm p-2 border-r border-gray-300 focus:outline-none cursor-pointer rounded-l-full"
          >
            <option value="All">All</option>
            <option v-for="category in categories" :key="category.id" :value="category.slug">
              {{ category.name }}
            </option>
          </select>

          <!-- Search Input with Animated Placeholder -->
          <input
            type="text"
            v-model="searchQuery"
            @input="debouncedSearch"
            class="flex-1 text-[#1c1c1c] border-none text-sm focus:outline-none px-3 py-2"
            :placeholder="animatedPlaceholder"
          />

          <!-- Search Button -->
          <button
            @click="filterBySearch"
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
import { useRouter } from 'vue-router';
import { useEquipmentsStore } from '@/store/equipments';
import { debounce } from 'lodash';

const router = useRouter();
const store = useEquipmentsStore();

const searchQuery = ref('');
const selectedCategory = ref('All');
const animatedPlaceholder = ref('');
const itemsToType = ["Camera", "Laptop", "Projector", "Drone", "Lighting Kit"];
let itemIndex = 0;

// Fetch categories and equipments on mount
onMounted(() => {
  store.fetchCategories();
  store.fetchEquipments();
  cycleTypingEffect();
});

// Computed property for categories
const categories = computed(() => store.categories);

// Handle category change
const handleCategoryChange = async () => {
  if (selectedCategory.value === 'All') {
    searchQuery.value = '';
    store.searchQuery = '';
    router.push('/');
    await store.fetchEquipments();
    store.filteredEquipments = store.equipments;
  } else {
    router.push({ name: 'category-details', query: { cat: selectedCategory.value } });
  }
};

// Function to update search query
const filterBySearch = () => {
  store.searchQuery = searchQuery.value;
};

// Debounced search to avoid filtering on every keystroke
const debouncedSearch = debounce(filterBySearch, 700);

// Typing effect for placeholder
const cycleTypingEffect = async () => {
  while (true) {
    const text = itemsToType[itemIndex];
    animatedPlaceholder.value = "";
    
    // Type text
    for (let i = 0; i < text.length; i++) {
      await new Promise(resolve => setTimeout(() => {
        animatedPlaceholder.value += text[i];
        resolve();
      }, 150));
    }

    // Wait before deleting
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Delete text
    while (animatedPlaceholder.value.length > 0) {
      await new Promise(resolve => setTimeout(() => {
        animatedPlaceholder.value = animatedPlaceholder.value.slice(0, -1);
        resolve();
      }, 100));
    }

    // Move to next item
    itemIndex = (itemIndex + 1) % itemsToType.length;
  }
};
</script>
