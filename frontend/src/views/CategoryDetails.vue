<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import Hero from '@/components/Hero.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import Card from '@/components/Card.vue';
import EmptyList from '@/components/Empty.vue';
import { useEquipmentsStore } from '@/store/equipments';

const route = useRoute();
const store = useEquipmentsStore();

const filteredEquipments = ref([]);
const categoryEquipments = ref([]); // Store category-filtered items separately
const categoryMap = ref({});

// Get search query from store (computed)
const searchQuery = computed(() => store.searchQuery);

// Watch store.categories and update categoryMap
watch(() => store.categories, (newCategories) => {
  categoryMap.value = newCategories.reduce((map, category) => {
    map[category.slug] = category.id;
    return map;
  }, {});
}, { immediate: true });

// Fetch categories and equipment data
const fetchData = async () => {
  await store.fetchCategories();
  await store.fetchEquipments();
  filterByCategory();
};

// **Fix: Ensure category filtering works correctly**
const filterByCategory = () => {
  const categorySlug = route.query.cat;
  const categoryId = categoryMap.value[categorySlug];

  console.log("Selected categorySlug:", categorySlug);
  console.log("Resolved categoryId:", categoryId);
  console.log("Category Map:", categoryMap.value);
  
  if (!categoryId) {
    console.error('❌ No matching category ID found for slug:', categorySlug);
    categoryEquipments.value = [];
    filteredEquipments.value = [];
    return;
  }

  // Ensure `equipment.category` contains the correct ID format
  categoryEquipments.value = store.equipments.filter(equipment => {
    console.log("Equipment category:", equipment.category, "| Expected categoryId:", categoryId);
    return equipment.category === categoryId;
  });

  console.log("Filtered Equipment Count:", categoryEquipments.value.length);
  applySearch();
};

// Apply search on top of category-filtered results
const applySearch = () => {
  if (!searchQuery.value) {
    filteredEquipments.value = categoryEquipments.value;
    return;
  }

  const query = searchQuery.value.toLowerCase();
  filteredEquipments.value = categoryEquipments.value.filter(equipment => (
    equipment.name.toLowerCase().includes(query) ||
    (equipment.description && equipment.description.toLowerCase().includes(query)) ||
    equipment.hourly_rate.toString().includes(query) ||
    (equipment.address?.street_address && equipment.address.street_address.toLowerCase().includes(query)) ||
    (equipment.address?.city && equipment.address.city.toLowerCase().includes(query)) ||
    (equipment.address?.state && equipment.address.state.toLowerCase().includes(query))
  ));
};

// Watch for route changes and re-filter by category
watch(() => route.query.cat, filterByCategory);

// Watch for search query changes and apply search filtering
watch(searchQuery, applySearch);

// Fetch categories & equipment when mounted
onMounted(fetchData);
</script>

<template>
  <Hero />
  <Breadcrumb />

  <!-- Show empty state if no equipment is found -->
  <EmptyList v-if="filteredEquipments.length === 0" />

  <!-- Equipment List -->
  <div class="p-2 w-full hidden md:block" v-if="filteredEquipments.length > 0">
    <Card :equipments="filteredEquipments" />
  </div>

  <div class="p-2 w-full text-xs md:hidden" v-if="filteredEquipments.length > 0">
    <Card :equipments="filteredEquipments" />
  </div>
</template>

<style scoped>
/* Additional styles can go here if needed */
</style>
