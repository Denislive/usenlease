<template>
  <div class="hidden md:block">
    <h1 class="text-xl font-bold mb-4">
      <i class="pi pi-filter"></i> Filters
    </h1>
    <ul class="space-y-4">
      <!-- Category Filter -->
      <li class="product-filters-tab">
        <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Category</a>
        <ul class="ml-4 space-y-2 overflow-y-auto max-h-64">
          <li>
            <a href="#" class="text-xl text-gray-500" @click.prevent="clearAll('category')">Clear All</a>
          </li>
          <li v-for="(category, index) in displayedCategories" :key="category.id">
            <input
              :id="`category-checkbox${category.id}`"
              type="checkbox"
              class="mr-2"
              v-model="selectedCategories[category.name]"
            />
            <label :for="`category-checkbox${category.id}`" class="text-xl">{{ category.name }}</label>
          </li>
        </ul>
        <button v-if="categories.length > 20" @click="toggleShowMore('category')" class="text-blue-500 mt-2">
          {{ showMoreCategories ? 'Show Less' : 'Show More' }}
        </button>
      </li>

      <!-- Location Filter -->
      <li class="product-filters-tab">
        <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Location</a>
        <ul class="ml-4 space-y-2 overflow-y-auto max-h-64">
          <li>
            <a href="#" class="text-xl text-gray-500" @click.prevent="clearAll('location')">Clear All</a>
          </li>
          <li v-for="(city, index) in displayedCities" :key="index">
            <input
              :id="`city-checkbox${index}`"
              type="checkbox"
              class="mr-2"
              v-model="selectedCities[city]"
            />
            <label :for="`city-checkbox${city}`" class="text-xl">{{ city }}</label>
          </li>
        </ul>
        <button v-if="cities.length > 20" @click="toggleShowMore('location')" class="text-blue-500 mt-2">
          {{ showMoreCities ? 'Show Less' : 'Show More' }}
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

// Props
const props = defineProps({
  categories: {
    type: Array,
    required: true,
  },
  cities: {
    type: Array,
    required: true,
  },
  selectedCategories: {
    type: Object,
    required: true,
  },
  selectedCities: {
    type: Object,
    required: true,
  },
});

// State for showing more categories and cities
const showMoreCategories = ref(false);
const showMoreCities = ref(false);

// Computed properties for displaying categories and cities
const displayedCategories = computed(() =>
  showMoreCategories.value ? props.categories : props.categories.slice(0, 20)
);
const displayedCities = computed(() =>
  showMoreCities.value ? props.cities : props.cities.slice(0, 20)
);

// Toggle show more/less
const toggleShowMore = (type) => {
  if (type === 'category') {
    showMoreCategories.value = !showMoreCategories.value;
  } else if (type === 'location') {
    showMoreCities.value = !showMoreCities.value;
  }
};

// Function to clear all selected filters
const clearAll = (filterType) => {
  if (filterType === 'category') {
    Object.keys(props.selectedCategories).forEach((key) => {
      props.selectedCategories[key] = false;
    });
  } else if (filterType === 'location') {
    Object.keys(props.selectedCities).forEach((key) => {
      props.selectedCities[key] = false;
    });
  }
};
</script>

<style scoped>
.overflow-y-auto {
  overflow-y: auto;
}
.max-h-64 {
  max-height: 16rem; /* Adjust as needed */
}
</style>
