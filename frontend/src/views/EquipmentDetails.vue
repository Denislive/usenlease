<template>
  <main>
    <div class="mx-auto p-2 w-6/8 sm:w-11/12">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-4 p-1">
        <!-- Sidebar Section -->
        <aside class="md:col-span-8 bg-gray-100 rounded p-2">
          <EquipmentImage :equipment="equipment" />
        </aside>

        <!-- Main Content Section -->
        <main class="md:col-span-4 bg-gray-100 p-1">
          <EquipmentDetails :equipment="equipment" :loading="loading" :error="error" />
        </main>
      </div>
      <EquipmentTabs :equipment="equipment" />
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import Hero from '@/components/Hero.vue';
import EquipmentImage from '@/components/EquipmentImage.vue';
import EquipmentDetails from '@/components/EquipmentDetails.vue';
import EquipmentTabs from '@/components/EquipmentTabs.vue';

const equipment = ref(null);
const loading = ref(true);
const error = ref(null);
const route = useRoute();
const api_base_url = import.meta.env.VITE_API_BASE_URL;


const fetchEquipment = async () => {
  const equipmentId = route.params.id; // Get the equipment ID from the route
  try {
    const response = await fetch(`${api_base_url}/api/equipments/${equipmentId}/`); // Adjust the URL based on your API
    if (!response.ok) throw new Error('Failed to fetch equipment details');
    equipment.value = await response.json();
  } catch (err) {
    error.value = err.message; // Capture the error message
  } finally {
    loading.value = false; // Set loading to false regardless of success or error
  }
};

onMounted(fetchEquipment);
</script>

<style scoped>
/* Additional styles can go here if needed */
</style>
