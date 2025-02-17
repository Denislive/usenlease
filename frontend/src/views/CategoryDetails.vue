<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import Hero from '@/components/Hero.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import Card from '@/components/Card.vue';
import EmptyList from '@/components/Empty.vue';

import { useStore } from 'vuex';

const route = useRoute();
const equipmentList = ref([]);
const filteredEquipments = ref([]);
const categoryMap = ref({});

const search = useStore();

const searchQuery = computed(() => search.getters.getSearchQuery);

const api_base_url = import.meta.env.VITE_API_BASE_URL;

const fetchCategories = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/categories/`);
    response.data.forEach(category => {
      categoryMap.value[category.slug] = category.id;
    });
  } catch (error) {
    console.error('Error fetching category data:', error);
  }
};

const fetchEquipments = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/equipments/`);
    equipmentList.value = response.data;
    filterEquipments();
  } catch (error) {
    console.error('Error fetching equipment data:', error);
  }
};

const filterEquipments = () => {
  const categorySlug = route.query.cat;
  const categoryId = categoryMap.value[categorySlug];
  if (!categoryId) {
    console.error('No matching category ID found for slug:', categorySlug);
    return;
  }

  filteredEquipments.value = equipmentList.value.filter(equipment => {
    const matchesCategory = equipment.category === categoryId;

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      const matchesSearch = (
        equipment.name.toLowerCase().includes(query) ||
        equipment.description.toLowerCase().includes(query) ||
        equipment.hourly_rate.toString().includes(query) ||
        (equipment.address.street_address && equipment.address.street_address.toLowerCase().includes(query)) ||
        (equipment.address.city && equipment.address.city.toLowerCase().includes(query)) ||
        (equipment.address.state && equipment.address.state.toLowerCase().includes(query))
      );
      return matchesCategory && matchesSearch;
    }

    return matchesCategory;
  });
};

// Watch for changes in the route to reapply filters
watch(route, () => {
  filterEquipments();
});

// Watch for changes in the search query to reapply filters
watch(searchQuery, () => {
  filterEquipments();
});

onMounted(async () => {
  await fetchCategories();
  await fetchEquipments();
});
</script>

<template>
  <Hero />
  <Breadcrumb />

  <!-- Check if the equipment list is empty -->
  <EmptyList v-if="filteredEquipments.length === 0" />

  <!-- Render equipment for larger screens -->
  <div class="p-2 w-full hidden md:block" v-if="filteredEquipments.length > 0">
    <Card :equipments="filteredEquipments" />
  </div>

  <!-- Render equipment for smaller screens -->
  <div class="p-2 w-full text-xs md:hidden" v-if="filteredEquipments.length > 0">
    <Card :equipments="filteredEquipments" />
  </div>
</template>

<style scoped>
/* Additional styles can go here if needed */
</style>
