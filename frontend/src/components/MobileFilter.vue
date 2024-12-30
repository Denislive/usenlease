<template>
  <div class="md:hidden">
    <!-- Filters Button -->
    <button 
      @click="toggleFilters" 
      class="w-full text-xl font-bold mb-1 flex items-center justify-center bg-[#1c1c1c] text-white rounded-md py-2 hover:bg-[#ffc107] hover:text-[#1c1c1c] transition"
    >
      <i class="pi pi-filter mr-2"></i> Filters
    </button>

    <!-- Filters Panel -->
    <div v-if="showFilters" class="border border-gray-300 rounded-lg p-1 shadow-md bg-white mb-4">
      <ul class="space-y-2">
        <!-- Category Filter -->
        <li class="product-filters-tab">
          <a href="#" class="text-lg font-semibold text-gray-800 hover:text-blue-600 transition">
            Category
          </a>
          <ul class="ml-4 mt-1 space-y-1">
            <!-- Clear All -->
            <li>
              <a 
                href="#" 
                class="text-sm font-medium text-red-500 hover:underline transition" 
                @click="clearAll('mobileCategory')" 
                id="category-clear-all"
              >
                Clear All
              </a>
            </li>
            <!-- Category Items -->
            <li 
              v-for="category in mobileCategories" 
              :key="category.id" 
              class="flex items-center cursor-pointer bg-gray-100 hover:bg-gray-200 rounded-md px-2 py-1 transition"
              @click="toggleCategory(category.name)" 
            >
              <input 
                type="checkbox" 
                :id="'mobile-category-checkbox' + category.id" 
                :value="category.name" 
                v-model="mobileSelectedCategories[category.name]"
                @change="applyFilters"
                class="hidden" 
              />
              <label :for="'mobile-category-checkbox' + category.id" class="flex items-center space-x-3">
                <span 
                  :class="{
                    'pi pi-check-circle text-[#1c1c1c]': mobileSelectedCategories[category.name],
                    'pi pi-circle text-gray-400': !mobileSelectedCategories[category.name]
                  }"
                  class="text-xl"
                ></span>
                <span class="text-gray-700 text-lg font-medium">
                  {{ category.name }}
                </span>
              </label>
            </li>
          </ul>
        </li>

        <!-- Location Filter -->
        <li class="product-filters-tab">
          <a href="#" class="text-lg font-semibold text-gray-800 hover:text-blue-600 transition">
            Location
          </a>
          <ul class="ml-4 mt-1 space-y-1">
            <!-- Clear All -->
            <li>
              <a 
                href="#" 
                class="text-sm font-medium text-red-500 hover:underline transition" 
                @click="clearAll('mobileLocation')" 
                id="location-clear-all"
              >
                Clear All
              </a>
            </li>
            <!-- Location Items -->
            <li 
              v-for="(city, index) in mobileCities" 
              :key="index" 
              class="flex items-center cursor-pointer bg-gray-100 hover:bg-gray-200 rounded-md px-2 py-1 transition"
              @click="toggleLocation(city)" 
            >
              <input 
                type="checkbox" 
                :id="'mobile-city-checkbox' + index" 
                :value="city" 
                v-model="mobileSelectedCities[city]"
                @change="applyFilters"
                class="hidden" 
              />
              <label :for="'mobile-city-checkbox' + index" class="flex items-center space-x-3">
                <span 
                  :class="{
                    'pi pi-check-circle text-[#1c1c1c]': mobileSelectedCities[city],
                    'pi pi-circle text-gray-400': !mobileSelectedCities[city]
                  }"
                  class="text-xl"
                ></span>
                <span class="text-gray-700 text-lg font-medium">
                  {{ city }}
                </span>
              </label>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Props
const props = defineProps({
  mobileCategories: {
    type: Array,
    required: true,
  },
  mobileCities: {
    type: Array,
    required: true,
  },
  mobileSelectedCategories: {
    type: Object,
    required: true,
  },
  mobileSelectedCities: {
    type: Object,
    required: true,
  },
});

// States
const showFilters = ref(false);

// Function to toggle the filters panel visibility
const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

// Function to clear all selected filters
const clearAll = (filterType) => {
  if (filterType === 'mobileCategory') {
    Object.keys(props.mobileSelectedCategories).forEach((key) => {
      props.mobileSelectedCategories[key] = false;
    });
  } else if (filterType === 'mobileLocation') {
    Object.keys(props.mobileSelectedCities).forEach((key) => {
      props.mobileSelectedCities[key] = false;
    });
  }
};

// Function to apply filters (for future use, e.g., with an API request)
const applyFilters = () => {
  // Add logic to apply the filters, such as sending them to an API
};

// Function to toggle the category selection
const toggleCategory = (categoryName) => {
  props.mobileSelectedCategories[categoryName] = !props.mobileSelectedCategories[categoryName];
};

// Function to toggle the location selection
const toggleLocation = (city) => {
  props.mobileSelectedCities[city] = !props.mobileSelectedCities[city];
};
</script>
