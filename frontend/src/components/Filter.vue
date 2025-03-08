<template>
  <div class="hidden md:block">
    <h1 class="text-lg font-bold mb-4">
      <i class="pi pi-filter"></i> Filters
    </h1>
    <ul class="space-y-4">
      <!-- Category Filter -->
      <li class="product-filters-tab">
        <a href="#" class="text-base font-semibold hover:text-[#1c1c1c]">Category</a>
        <ul v-if="displayedCategories.length" class="ml-4 space-y-2 overflow-y-auto max-h-64">
          <li>
            <a href="#" class="text-sm text-gray-500" @click.prevent="clearAll('category')">Clear All</a>
          </li>
          <li v-for="category in displayedCategories" :key="category.name">
            <input
              :id="`category-checkbox-${slugify(category.name)}`"
              type="checkbox"
              class="mr-2"
              v-model="selectedCategories[category.name]"
              @change="handleFilterChange"
            />
            <label :for="`category-checkbox-${slugify(category.name)}`" class="text-sm">{{ category.name }}</label>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500 ml-4">No categories available.</p>
        <button v-if="categories.length > 20" @click="toggleShowMore('category')" class="text-blue-500 mt-2 text-sm">
          {{ showMoreCategories ? 'Show Less' : 'Show More' }}
        </button>
      </li>

      <!-- Location Filter -->
      <li class="product-filters-tab">
        <a href="#" class="text-base font-semibold hover:text-[#1c1c1c]">Location</a>
        <ul v-if="displayedCities.length" class="ml-4 space-y-2 overflow-y-auto max-h-64">
          <li>
            <a href="#" class="text-sm text-gray-500" @click.prevent="clearAll('location')">Clear All</a>
          </li>
          <li v-for="city in displayedCities" :key="city">
            <input
              :id="`city-checkbox-${city}`"
              type="checkbox"
              class="mr-2"
              v-model="selectedCities[city]"
              @change="handleFilterChange"
            />
            <label :for="`city-checkbox-${city}`" class="text-sm">{{ city }}</label>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500 ml-4">No cities available.</p>
        <button v-if="cities.length > 20" @click="toggleShowMore('location')" class="text-blue-500 mt-2 text-sm">
          {{ showMoreCities ? 'Show Less' : 'Show More' }}
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useEquipmentsStore } from '@/store/equipments';

// ✅ Function to slugify only category names
const slugify = (text) => {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')   // Replace spaces with -
    .replace(/[^\w-]+/g, '') // Remove all non-word characters
    .replace(/--+/g, '-');  // Replace multiple - with single -
};

const props = defineProps({
  categories: {
    type: Array,
    required: true
  },
  cities: {
    type: Array,
    required: true
  }
});

const store = useEquipmentsStore();
const selectedCategories = ref({});
const selectedCities = ref({});

const showMoreCategories = ref(false);
const showMoreCities = ref(false);

const displayedCategories = ref(props.categories.slice(0, 20));
const displayedCities = ref(props.cities.slice(0, 20));

// ✅ Ensure displayed lists update when props change
watch(() => props.categories, (newCategories) => {
  displayedCategories.value = showMoreCategories.value ? newCategories : newCategories.slice(0, 20);
}, { immediate: true });

watch(() => props.cities, (newCities) => {
  displayedCities.value = showMoreCities.value ? newCities : newCities.slice(0, 20);
}, { immediate: true });

// ✅ Convert selected categories (slugified) but keep cities as they are
const getSelectedCategories = computed(() => {
  return Object.keys(selectedCategories.value)
    .filter(name => selectedCategories.value[name])
    .map(slugify);
});

const getSelectedCities = computed(() => {
  return Object.keys(selectedCities.value)
    .filter(name => selectedCities.value[name]);
});

// ✅ Function to handle filter changes and update `filteredEquipments`
const handleFilterChange = () => {
  store.fetchFilteredEquipments({
    categories: getSelectedCategories.value,
    cities: getSelectedCities.value
  });
};

// ✅ Toggle Show More
const toggleShowMore = (type) => {
  if (type === 'category') {
    showMoreCategories.value = !showMoreCategories.value;
    displayedCategories.value = showMoreCategories.value ? props.categories : props.categories.slice(0, 20);
  } else if (type === 'location') {
    showMoreCities.value = !showMoreCities.value;
    displayedCities.value = showMoreCities.value ? props.cities : props.cities.slice(0, 20);
  }
};

// ✅ Clear all filters and re-filter
const clearAll = (filterType) => {
  if (filterType === 'category') {
    selectedCategories.value = {};
  } else if (filterType === 'location') {
    selectedCities.value = {};
  }
  store.fetchFilteredEquipments({
    categories: getSelectedCategories.value,
    cities: getSelectedCities.value
  });
};

// ✅ Watch for changes in selected filters
watch([selectedCategories, selectedCities], () => {
  store.fetchFilteredEquipments({
    categories: getSelectedCategories.value,
    cities: getSelectedCities.value
  });
}, { deep: true });
</script>
