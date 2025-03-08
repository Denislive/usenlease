<template>
  <Hero />
  <Breadcrumb />

  <div class="w-full mx-4 hidden md:block">
    <div class="grid grid-cols-12 gap-4 p-1">
      <!-- Sidebar Section -->
      <aside class="col-span-2 bg-gray-100 rounded p-2">
        <Filter 
          :categories="categories"
          :cities="cities"
          :selectedCategories="selectedCategories"
          :selectedCities="selectedCities"
          @update:selectedCategories="updateSelectedCategories"
          @update:selectedCities="updateSelectedCities"
        />
      </aside>

      <!-- Main Content Section -->
      <main class="col-span-10 bg-gray-100 p-1">
        <Card :equipments="equipments" />
      </main>
    </div>
  </div>

  <div class="p-2 w-full text-xs md:hidden">
    <MobileFilter 
      :categories="categories" 
      :cities="cities" 
      :selectedCategories="selectedCategories"
      :selectedCities="selectedCities"
      @update:selectedCategories="updateSelectedCategories"
      @update:selectedCities="updateSelectedCities"
    />
    <Card :equipments="equipments" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useEquipmentsStore } from '@/store/equipments';
import Hero from '@/components/Hero.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import Filter from '@/components/Filter.vue';
import Card from '@/components/Card.vue';
import MobileFilter from '@/components/MobileFilter.vue';

const equipmentStore = useEquipmentsStore();

// Reactive states from Pinia store
const equipments = computed(() => equipmentStore.equipments);
const categories = computed(() => equipmentStore.categories);
const searchQuery = computed(() => equipmentStore.searchQuery);

// ✅ Make selected categories and cities reactive
const selectedCategories = ref({});
const selectedCities = ref({});

// Extract unique cities from the equipments
const cities = computed(() => {
  return [...new Set(equipments.value.map(e => e.address?.city).filter(city => city))];
});

// Fetch data when component mounts
onMounted(() => {
  equipmentStore.fetchFilteredEquipments({ 
    search: searchQuery.value, 
    categories: [],
    cities: []
  });
  equipmentStore.fetchCategories();
});

// ✅ Update selected categories
const updateSelectedCategories = (newSelection) => {
  selectedCategories.value = newSelection;
  fetchFilteredEquipments();
};

// ✅ Update selected cities
const updateSelectedCities = (newSelection) => {
  selectedCities.value = newSelection;
  fetchFilteredEquipments();
};

// ✅ Fetch filtered equipments from the store
const fetchFilteredEquipments = () => {
  const params = {
    search: searchQuery.value || '',
    categories: Object.keys(selectedCategories.value).filter(key => selectedCategories.value[key]),
    cities: Object.keys(selectedCities.value).filter(key => selectedCities.value[key])
  };

  equipmentStore.fetchFilteredEquipments(params);
};

// ✅ Watch for changes in filters and trigger fetching
watch([selectedCategories, selectedCities, searchQuery], fetchFilteredEquipments);
</script>
