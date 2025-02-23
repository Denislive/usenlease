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

const categoryEquipments = ref([]); // To store filtered equipments
const categoryMap = ref({}); // To store category mapping

console.log(`[INIT] Component setup initialized.`);

// ✅ Computed property for search query
const searchQuery = computed(() => store.searchQuery);

// ✅ Computed `filteredEquipments`
const filteredEquipments = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  console.log(`[SEARCH] Filtering equipments with query: "${query}"`);

  const results = categoryEquipments.value.filter(equipment => (
    equipment.name.toLowerCase().includes(query) ||
    (equipment.description && equipment.description.toLowerCase().includes(query)) ||
    equipment.hourly_rate.toString().includes(query) ||
    (equipment.address?.street_address && equipment.address.street_address.toLowerCase().includes(query)) ||
    (equipment.address?.city && equipment.address.city.toLowerCase().includes(query)) ||
    (equipment.address?.state && equipment.address.state.toLowerCase().includes(query))
  ));

  console.log(`[SEARCH] Found ${results.length} matching equipments.`);
  return results;
});

// ✅ Function to filter equipment by category
const filterByCategory = () => {
  const categorySlug = route.query.cat;
  const categoryId = categoryMap.value[categorySlug];

  console.log(`[CATEGORY FILTER] Slug: ${categorySlug}, Resolved ID: ${categoryId}`);

  if (!categoryId) {
    console.warn(`[CATEGORY FILTER] No matching category found! Clearing equipments.`);
    categoryEquipments.value = [];
    return;
  }

  categoryEquipments.value = store.equipments.filter(equipment => {
    const equipmentCategoryId = typeof equipment.category === 'object' ? equipment.category.id : equipment.category;
    return equipmentCategoryId === categoryId;
  });

  console.log(`[CATEGORY FILTER] Equipment found: ${categoryEquipments.value.length}`);
  store.filteredEquipments = categoryEquipments.value;
};

// ✅ Watch for category changes in URL
watch(() => route.query.cat, () => {
  console.log(`[WATCH] Category in URL changed to: ${route.query.cat}`);
  filterByCategory();
}, { immediate: true });

// ✅ Watch `store.categories` to build category mapping
watch(() => store.categories, (newCategories) => {
  console.log(`[WATCH] Categories updated. Rebuilding category mapping.`);
  categoryMap.value = newCategories.reduce((map, category) => {
    map[category.slug] = category.id;
    return map;
  }, {});

  console.log(`[WATCH] Category Map Built:`, categoryMap.value);
  filterByCategory(); // Ensure filtering happens after categories are loaded
}, { immediate: true });

// ✅ Fetch categories & equipment on mount
const fetchData = async () => {
  console.log(`[MOUNTED] Checking if data needs to be fetched...`);

  if (store.equipments.length === 0) {
    console.log(`[MOUNTED] Fetching categories and equipments...`);
    await store.fetchCategories();
    await store.fetchEquipments();
    console.log(`[MOUNTED] Data fetched successfully.`);
  } else {
    console.log(`[MOUNTED] Data already exists. Skipping fetch.`);
  }
};

// Run fetch on mounted
onMounted(fetchData);
</script>

<template>
  <Hero />
  <Breadcrumb />

  <!-- Show empty state if no equipment is found -->
  <EmptyList v-if="filteredEquipments.length === 0" />

  <!-- Equipment List -->
  <div class="p-2 w-full hidden md:block" v-if="filteredEquipments.length > 0">
    <Card />
  </div>

  <div class="p-2 w-full text-xs md:hidden" v-if="filteredEquipments.length > 0">
    <Card />
  </div>
</template>
