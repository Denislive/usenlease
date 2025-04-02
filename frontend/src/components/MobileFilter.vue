<template>
  <div class="md:hidden">
    <!-- Filters Toggle Button -->
    <button
      @click="toggleFilters"
      class="w-full text-sm font-bold mb-1 flex items-center justify-center bg-[#1c1c1c] text-white rounded-md py-2 hover:bg-[#ffc107] hover:text-[#1c1c1c] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-[#ffc107]"
      :aria-expanded="showFilters"
      aria-controls="mobile-filters-panel"
    >
      <i class="pi pi-filter mr-2" aria-hidden="true"></i>
      <span>{{ showFilters ? 'Hide Filters' : 'Filter Items' }}</span>
    </button>

    <!-- Filters Panel -->
    <div 
      v-if="showFilters" 
      id="mobile-filters-panel"
      class="border border-gray-200 rounded-lg p-4 shadow-md bg-white mb-4"
    >
      <ul class="space-y-4">
        <!-- Category Filter -->
        <li class="product-filters-tab">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">
            Category
          </h3>
          <ul v-if="displayedCategories.length" class="ml-2 mt-2 space-y-2">
            <li>
              <button 
                @click.prevent="clearAll('category')"
                class="text-sm font-medium text-red-500 hover:underline transition-colors focus:outline-none"
                aria-label="Clear all category filters"
              >
                Clear All
              </button>
            </li>
            <li 
              v-for="category in displayedCategories" 
              :key="`mobile-cat-${category.name}`"
              class="group"
            >
              <input
                :id="`mobile-category-checkbox-${slugify(category.name)}`"
                type="checkbox"
                class="sr-only"
                v-model="selectedCategories[category.name]"
                @change="handleFilterChange"
              />
              <label
                :for="`mobile-category-checkbox-${slugify(category.name)}`"
                class="flex items-center space-x-3 cursor-pointer px-3 py-2 rounded-md transition-colors duration-200 group-hover:bg-gray-100"
                :class="{ 'bg-gray-100': selectedCategories[category.name] }"
              >
                <span
                  :class="{
                    'pi pi-check-circle text-[#1c1c1c]': selectedCategories[category.name],
                    'pi pi-circle text-gray-400': !selectedCategories[category.name]
                  }"
                  class="text-xl"
                  aria-hidden="true"
                ></span>
                <span class="text-gray-700 text-base font-medium">
                  {{ category.name }}
                </span>
              </label>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500 ml-2">
            No categories available
          </p>
          <button
            v-if="categories.length > SHOW_MORE_THRESHOLD"
            @click="toggleShowMore('category')"
            class="text-blue-500 hover:text-blue-700 mt-2 text-sm focus:outline-none"
            :aria-expanded="showMoreCategories"
          >
            {{ showMoreCategories ? 'Show Less' : 'Show More' }}
          </button>
        </li>

        <!-- Location Filter -->
        <li class="product-filters-tab">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">
            Location
          </h3>
          <ul v-if="displayedCities.length" class="ml-2 mt-2 space-y-2">
            <li>
              <button
                @click.prevent="clearAll('location')"
                class="text-sm font-medium text-red-500 hover:underline transition-colors focus:outline-none"
                aria-label="Clear all location filters"
              >
                Clear All
              </button>
            </li>
            <li
              v-for="city in displayedCities"
              :key="`mobile-loc-${city}`"
              class="group"
            >
              <input
                :id="`mobile-city-checkbox-${slugify(city)}`"
                type="checkbox"
                class="sr-only"
                v-model="selectedCities[city]"
                @change="handleFilterChange"
              />
              <label
                :for="`mobile-city-checkbox-${slugify(city)}`"
                class="flex items-center space-x-3 cursor-pointer px-3 py-2 rounded-md transition-colors duration-200 group-hover:bg-gray-100"
                :class="{ 'bg-gray-100': selectedCities[city] }"
              >
                <span
                  :class="{
                    'pi pi-check-circle text-[#1c1c1c]': selectedCities[city],
                    'pi pi-circle text-gray-400': !selectedCities[city]
                  }"
                  class="text-xl"
                  aria-hidden="true"
                ></span>
                <span class="text-gray-700 text-base font-medium">
                  {{ city }}
                </span>
              </label>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500 ml-2">
            No cities available
          </p>
          <button
            v-if="cities.length > SHOW_MORE_THRESHOLD"
            @click="toggleShowMore('location')"
            class="text-blue-500 hover:text-blue-700 mt-2 text-sm focus:outline-none"
            :aria-expanded="showMoreCities"
          >
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

// Constants
const SHOW_MORE_THRESHOLD = 20;

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

// State
const showFilters = ref(false);
const showMoreCategories = ref(false);
const showMoreCities = ref(false);
const selectedCategories = ref({});
const selectedCities = ref({});

// Computed
const displayedCategories = computed(() => 
  showMoreCategories.value 
    ? props.categories 
    : props.categories.slice(0, SHOW_MORE_THRESHOLD)
);

const displayedCities = computed(() => 
  showMoreCities.value 
    ? props.cities 
    : props.cities.slice(0, SHOW_MORE_THRESHOLD)
);

const getSelectedCategories = computed(() => 
  Object.entries(selectedCategories.value)
    .filter(([_, isSelected]) => isSelected)
    .map(([name]) => slugify(name))
);

const getSelectedCities = computed(() => 
  Object.entries(selectedCities.value)
    .filter(([_, isSelected]) => isSelected)
    .map(([name]) => name)
);

// Watchers
watch(() => props.categories, (newCategories) => {
  newCategories.forEach(cat => {
    if (!(cat.name in selectedCategories.value)) {
      selectedCategories.value[cat.name] = false;
    }
  });
}, { immediate: true });

watch(() => props.cities, (newCities) => {
  newCities.forEach(city => {
    if (!(city in selectedCities.value)) {
      selectedCities.value[city] = false;
    }
  });
}, { immediate: true });

watch([selectedCategories, selectedCities], () => {
  handleFilterChange();
}, { deep: true });

// Methods
const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

const toggleShowMore = (type) => {
  if (type === 'category') {
    showMoreCategories.value = !showMoreCategories.value;
  } else if (type === 'location') {
    showMoreCities.value = !showMoreCities.value;
  }
};

const handleFilterChange = () => {
  store.fetchFilteredEquipments({
    categories: getSelectedCategories.value,
    cities: getSelectedCities.value
  });
};

const clearAll = (filterType) => {
  if (filterType === 'category') {
    Object.keys(selectedCategories.value).forEach(key => {
      selectedCategories.value[key] = false;
    });
  } else if (filterType === 'location') {
    Object.keys(selectedCities.value).forEach(key => {
      selectedCities.value[key] = false;
    });
  }
};

const slugify = (text) => {
  if (typeof text !== 'string') return '';
  return text
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '');
};
</script>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.product-filters-tab {
  @apply border-b border-gray-200 pb-4 last:border-b-0 last:pb-0;
}

/* Smooth transitions */
[type='checkbox']:checked + label {
  @apply bg-gray-100;
}
</style>