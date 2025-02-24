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

const categoryEquipments = ref([]); // To store equipments filtered by category
const categoryMap = ref({}); // To store category mapping

// ✅ Computed property for search query
const searchQuery = computed(() => store.searchQuery);

// ✅ Computed `filteredEquipments` that updates dynamically
const filteredEquipments = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();

  // If search query is empty, return category filtered items
  if (query === '') {
    filterByCategory();
  }

  // Filter within the selected category based on search query
  return categoryEquipments.value.filter(equipment => (
    equipment.name.toLowerCase().includes(query) ||
    (equipment.description && equipment.description.toLowerCase().includes(query)) ||
    equipment.hourly_rate.toString().includes(query) ||
    (equipment.address?.street_address && equipment.address.street_address.toLowerCase().includes(query)) ||
    (equipment.address?.city && equipment.address.city.toLowerCase().includes(query)) ||
    (equipment.address?.state && equipment.address.state.toLowerCase().includes(query))
  ));
});

// ✅ Function to filter equipment by category
const filterByCategory = () => {
  const categorySlug = route.query.cat;
  const categoryId = categoryMap.value[categorySlug];

  console.log("Category Slug:", categorySlug);
  console.log("Resolved Category ID:", categoryId);

  if (!categoryId) {
    categoryEquipments.value = []; // Clear if no category matches
    return;
  }

  categoryEquipments.value = store.equipments.filter(equipment => {
    const equipmentCategoryId = typeof equipment.category === 'object' ? equipment.category.id : equipment.category;
    return equipmentCategoryId === categoryId;
  });

  console.log("Filtered Equipment Count:", categoryEquipments.value.length);
  store.filteredEquipments = categoryEquipments.value;
};

// ✅ Watch for category changes in URL & update `categoryEquipments`
watch(() => route.query.cat, filterByCategory, { immediate: true });

// ✅ Watch `store.categories` to build category mapping
watch(() => store.categories, (newCategories) => {
  categoryMap.value = newCategories.reduce((map, category) => {
    map[category.slug] = category.id;
    return map;
  }, {});

  // Ensure filtering runs after categories are loaded
  filterByCategory();
}, { immediate: true });

// ✅ Fetch categories & equipment on mount
const fetchData = async () => {
  if (store.equipments.length === 0) {
    await store.fetchCategories();
    await store.fetchEquipments();
    filterByCategory();
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
