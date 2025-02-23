<template>
  <section class="hero bg-gradient-to-r from-[#ff9e00] to-[#ffc107] py-2 lg:py-10 relative text-white overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-60"></div>
    
    <div class="container mx-auto text-center relative z-10 px-4">
      <h1 class="text-3xl lg:text-5xl font-bold leading-tight mb-6 animate__animated animate__fadeIn animate__delay-1s">
        Rent the Best Equipment for Your Needs
      </h1>
      <p class="text-sm text-black lg:text-xl mb-8 animate__animated animate__fadeIn animate__delay-2s">
        Find top-quality equipment for any project. Fast delivery and great customer support.
      </p>
      
      <div class="flex justify-center">
        <div class="w-full max-w-xl bg-white p-2 search shadow-lg">
          <div class="flex items-center">
            <div class="relative flex-shrink-0">
              <select
                v-model="selectedCategory"
                @change="goToCategory"
                class="bg-transparent text-[#1c1c1c] p-3 focus:outline-none cursor-pointer border-r border-gray-200"
              >
                <option value="All">All</option>
                <option v-for="category in categories" :key="category.id" :value="category.slug">
                  {{ category.name }}
                </option>
              </select>
            </div>
            
            <input
              type="text"
              class="flex-1 w-full text-[#1c1c1c] border-none text-lg focus:outline-none"
              placeholder="I am looking for ..."
              v-model="searchQuery"
              @input="debouncedSearch"
            />
            
            <button
              @click="filterBySearch"
              class="bg-[#ff6f00] text-white rounded-full px-4 py-3 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110"
            >
              <i class="pi pi-search text-lg"></i>
            </button>
          </div>
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

onMounted(() => {
  store.fetchCategories();
  store.fetchEquipments();
});

// Computed property for categories
const categories = computed(() => store.categories);

// Function to navigate to category details page
const goToCategory = () => {
  if (selectedCategory.value !== 'All') {
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

<style>
.search {
  border-radius: 5px;
}
.hero {
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
