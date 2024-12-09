<script setup>
import { defineProps } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  equipments: {
    type: Array,
    required: true,
  },
});

const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  const emptyStars = 5 - fullStars - halfStar;

  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(emptyStars);
};

const router = useRouter();

const api_base_url = import.meta.env.VITE_API_BASE_URL;


const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  }
};
</script>

<template>
  <div class="container mx-auto p-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <!-- Loop through the equipments -->
      <div
        v-for="equipment in props.equipments"
        :key="equipment.id"
        @click="() => { goToDetail(equipment.id) }"
        class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer"
      >
        <div class="relative">
          <!-- Availability Badge -->
          <span
            :class="{
              'bg-green-500': equipment.is_available,
              'bg-red-500': !equipment.is_available
            }"
            class="absolute top-2 left-2 text-white text-xs font-bold px-2 py-1 rounded flex items-center"
          >
            <i
              :class="{
                'pi pi-check-circle': equipment.is_available,
                'pi pi-times-circle': !equipment.is_available
              }"
              class="mr-1"
            ></i>
            {{ equipment.is_available ? 'Available' : 'Unavailable' }}
          </span>

          <!-- Equipment Image -->
          <img
            v-if="equipment.images.length > 0"
            :src="`${api_base_url}${equipment.images[0].image_url}`"
            :alt="equipment.images[0].image_url"
            class="w-full h-48 object-cover"
          />
          <img
            v-else
            src="https://via.placeholder.com/350"
            alt="Placeholder Image"
            class="w-full h-48 object-cover"
          />

        </div>

        <!-- Equipment Details -->
        <div class="p-4">
          <div class="text-left text-sm">
             <!-- reviews and rating -->
           <span class="rating text-yellow-500">{{ renderStars(equipment.rating) }}</span>
          <span class="reviews text-gray-600"> ({{ equipment.equipment_reviews ? equipment.equipment_reviews.length : 0 }} Reviews)</span>
      
          </div>
          
          <h5 class="text-xl font-semibold text-gray-800">{{ equipment.name }}</h5>
          <p class="text-[#ff9e00] text-lg">{{ equipment.hourly_rate }} / Hr</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Optional additional styles can go here */
</style>
