<template>
  <div class="md:hidden">
    <!-- Filters Button -->
    <button 
      @click="toggleFilters" 
      class="w-full text-sm font-bold mb-1 flex items-center justify-center bg-[#1c1c1c] text-white rounded-md py-2 hover:bg-[#ffc107] hover:text-[#1c1c1c] transition"
    >
      <i class="pi pi-filter mr-2"></i> Filters Items
    </button>

    <!-- Filters Panel -->
    <div v-if="showFilters" class="border border-gray-300 rounded-lg p-1 shadow-md bg-white mb-4">
      <ul class="space-y-2">
        <!-- Category Filter -->
        <li class="product-filters-tab">
          <a href="#" class="text-lg font-semibold text-gray-800 hover:text-blue-600 transition">
            Category
          </a>
          <ul v-if="displayedCategories.length" class="ml-4 mt-1 space-y-1">
            <li>
              <a href="#" class="text-sm font-medium text-red-500 hover:underline transition" @click.prevent="clearAll('category')">
                Clear All
              </a>
            </li>
            <li v-for="category in displayedCategories" :key="category.id">
              <input 
                :id="`mobile-category-checkbox-${category.id}`" 
                type="checkbox" 
                class="mr-2 hidden" 
                v-model="selectedCategories[category.id]"
                @change="handleFilterChange"
              />
              <label 
                :for="`mobile-category-checkbox-${category.id}`" 
                class="flex items-center space-x-3 cursor-pointer bg-gray-100 hover:bg-gray-200 rounded-md px-2 py-1 transition"
              >
                <span 
                  :class="{
                    'pi pi-check-circle text-[#1c1c1c]': selectedCategories[category.id],
                    'pi pi-circle text-gray-400': !selectedCategories[category.id]
                  }" 
                  class="text-xl"
                ></span>
                <span class="text-gray-700 text-lg font-medium">
                  {{ category.name }}
                </span>
              </label>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500 ml-4">No categories available.</p>
          <button v-if="categories.length > 20" @click="toggleShowMore('category')" class="text-blue-500 mt-2 text-sm">
            {{ showMoreCategories ? 'Show Less' : 'Show More' }}
          </button>
        </li>

        <!-- Location Filter -->
        <li class="product-filters-tab">
          <a href="#" class="text-lg font-semibold text-gray-800 hover:text-blue-600 transition">
            Location
          </a>
          <ul v-if="displayedCities.length" class="ml-4 mt-1 space-y-1">
            <li>
              <a href="#" class="text-sm font-medium text-red-500 hover:underline transition" @click.prevent="clearAll('location')">
                Clear All
              </a>
            </li>
            <li v-for="city in displayedCities" :key="city">
              <input 
                :id="`mobile-city-checkbox-${city}`" 
                type="checkbox" 
                class="mr-2 hidden" 
                v-model="selectedCities[city]"
                @change="handleFilterChange"
              />
              <label 
                :for="`mobile-city-checkbox-${city}`" 
                class="flex items-center space-x-3 cursor-pointer bg-gray-100 hover:bg-gray-200 rounded-md px-2 py-1 transition"
              >
                <span 
                  :class="{
                    'pi pi-check-circle text-[#1c1c1c]': selectedCities[city],
                    'pi pi-circle text-gray-400': !selectedCities[city]
                  }" 
                  class="text-xl"
                ></span>
                <span class="text-gray-700 text-lg font-medium">
                  {{ city }}
                </span>
              </label>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500 ml-4">No cities available.</p>
          <button v-if="cities.length > 20" @click="toggleShowMore('location')" class="text-blue-500 mt-2 text-sm">
            {{ showMoreCities ? 'Show Less' : 'Show More' }}
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useEquipmentsStore } from '@/store/equipments';

const props = defineProps({
  categories: {
    type: Array,
    required: true,
  },
  cities: {
    type: Array,
    required: true,
  },
});

const store = useEquipmentsStore();
const selectedCategories = store.selectedCategories;
const selectedCities = store.selectedCities;

const showFilters = ref(false);
const showMoreCategories = ref(false);
const showMoreCities = ref(false);

// ✅ Use computed properties to dynamically adjust displayed items
const displayedCategories = computed(() => {
  return showMoreCategories.value ? props.categories : props.categories.slice(0, 20);
});

const displayedCities = computed(() => {
  return showMoreCities.value ? props.cities : props.cities.slice(0, 20);
});

// ✅ Function to update filters
const handleFilterChange = () => {
  store.updateFilteredEquipments();
};

// ✅ Toggle filter visibility
const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

// ✅ Toggle Show More
const toggleShowMore = (type) => {
  if (type === 'category') {
    showMoreCategories.value = !showMoreCategories.value;
  } else if (type === 'location') {
    showMoreCities.value = !showMoreCities.value;
  }
};

// ✅ Clear all filters
const clearAll = (filterType) => {
  if (filterType === 'category') {
    Object.keys(selectedCategories).forEach(key => selectedCategories[key] = false);
  } else if (filterType === 'location') {
    Object.keys(selectedCities).forEach(key => selectedCities[key] = false);
  }
  store.updateFilteredEquipments();
};


// ✅ Watch for changes in selected filters
watch([selectedCategories, selectedCities], () => {
  store.updateFilteredEquipments();
}, { deep: true });

</script>
