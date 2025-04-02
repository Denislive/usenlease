<template>
  <div class="hidden md:block">
    <h1 class="text-lg font-bold mb-4">
      <i class="pi pi-filter"></i> Filters
    </h1>
    <ul class="space-y-4">
      <!-- Category Filter -->
      <li class="product-filters-tab">
        <button class="text-base font-semibold hover:text-[#1c1c1c] focus:outline-none">Category</button>
        <ul v-if="displayedCategories.length" class="ml-4 space-y-2 overflow-y-auto max-h-64">
          <li>
            <button class="text-sm text-gray-500 hover:underline focus:outline-none" @click.prevent="clearAll('category')">Clear All</button>
          </li>
          <li v-for="category in displayedCategories" :key="category.name">
            <input
              :id="`category-checkbox-${slugify(category.name)}`"
              type="checkbox"
              class="mr-2"
              :checked="selectedCategories[category.name]"
              @change="handleCheckboxChange($event, category.name, 'category')"
            />
            <label :for="`category-checkbox-${slugify(category.name)}`" class="text-sm cursor-pointer">{{ category.name }}</label>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500 ml-4">No categories available.</p>
        <button 
          v-if="categories.length > 20" 
          @click="toggleShowMore('category')" 
          class="text-blue-500 hover:text-blue-700 mt-2 text-sm focus:outline-none"
          :aria-expanded="showMoreCategories"
          :aria-controls="'category-filter-list'"
        >
          {{ showMoreCategories ? 'Show Less' : 'Show More' }}
        </button>
      </li>

      <!-- Location Filter -->
      <li class="product-filters-tab">
        <button class="text-base font-semibold hover:text-[#1c1c1c] focus:outline-none">Location</button>
        <ul v-if="displayedCities.length" class="ml-4 space-y-2 overflow-y-auto max-h-64">
          <li>
            <button class="text-sm text-gray-500 hover:underline focus:outline-none" @click.prevent="clearAll('location')">Clear All</button>
          </li>
          <li v-for="city in displayedCities" :key="city">
            <input
              :id="`city-checkbox-${city}`"
              type="checkbox"
              class="mr-2"
              :checked="selectedCities[city]"
              @change="handleCheckboxChange($event, city, 'location')"
            />
            <label :for="`city-checkbox-${city}`" class="text-sm cursor-pointer">{{ city }}</label>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500 ml-4">No cities available.</p>
        <button 
          v-if="cities.length > 20" 
          @click="toggleShowMore('location')" 
          class="text-blue-500 hover:text-blue-700 mt-2 text-sm focus:outline-none"
          :aria-expanded="showMoreCities"
          :aria-controls="'location-filter-list'"
        >
          {{ showMoreCities ? 'Show Less' : 'Show More' }}
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useEquipmentsStore } from '@/store/equipments';

// Constants
const SHOW_MORE_THRESHOLD = 20;
const INITIAL_DISPLAY_COUNT = 20;

// Slugify function with input validation
const slugify = (text) => {
  if (typeof text !== 'string') return '';
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-');
};

const props = defineProps({
  categories: {
    type: Array,
    required: true,
    validator: (value) => Array.isArray(value) && value.every(item => item?.name)
  },
  cities: {
    type: Array,
    required: true,
    validator: (value) => Array.isArray(value) && value.every(item => typeof item === 'string')
  }
});

const store = useEquipmentsStore();
const selectedCategories = ref({});
const selectedCities = ref({});

const showMoreCategories = ref(false);
const showMoreCities = ref(false);

const displayedCategories = ref([]);
const displayedCities = ref([]);

// Computed properties
const getSelectedCategories = computed(() => {
  return Object.entries(selectedCategories.value)
    .filter(([_, isSelected]) => isSelected)
    .map(([name]) => slugify(name));
});

const getSelectedCities = computed(() => {
  return Object.entries(selectedCities.value)
    .filter(([_, isSelected]) => isSelected)
    .map(([name]) => name);
});

// Methods
const handleCheckboxChange = (event, value, type) => {
  if (type === 'category') {
    selectedCategories.value = {
      ...selectedCategories.value,
      [value]: event.target.checked
    };
  } else if (type === 'location') {
    selectedCities.value = {
      ...selectedCities.value,
      [value]: event.target.checked
    };
  }
};

const handleFilterChange = () => {
  store.fetchFilteredEquipments({
    categories: getSelectedCategories.value,
    cities: getSelectedCities.value
  });
};

const toggleShowMore = (type) => {
  if (type === 'category') {
    showMoreCategories.value = !showMoreCategories.value;
    displayedCategories.value = showMoreCategories.value 
      ? props.categories 
      : props.categories.slice(0, INITIAL_DISPLAY_COUNT);
  } else if (type === 'location') {
    showMoreCities.value = !showMoreCities.value;
    displayedCities.value = showMoreCities.value 
      ? props.cities 
      : props.cities.slice(0, INITIAL_DISPLAY_COUNT);
  }
};

const clearAll = (filterType) => {
  if (filterType === 'category') {
    selectedCategories.value = {};
  } else if (filterType === 'location') {
    selectedCities.value = {};
  }
  handleFilterChange();
};

// Watchers
watch(() => props.categories, (newCategories) => {
  displayedCategories.value = showMoreCategories.value 
    ? newCategories 
    : newCategories.slice(0, INITIAL_DISPLAY_COUNT);
}, { immediate: true });

watch(() => props.cities, (newCities) => {
  displayedCities.value = showMoreCities.value 
    ? newCities 
    : newCities.slice(0, INITIAL_DISPLAY_COUNT);
}, { immediate: true });

watch([selectedCategories, selectedCities], handleFilterChange, { deep: true });
</script>