<template>
  <div class="bg-white rounded-xl shadow-md overflow-hidden transition-all hover:shadow-lg cursor-pointer flex flex-col h-full">
    <!-- Image container with fixed height -->
    <div class="relative h-48 w-full">
      <img 
        v-if="item.images?.length > 0"
        :src="getFullImageUrl(item.images[0].image_url)" 
        :alt="`Image of ${item.name}`"
        class="w-full h-full object-cover"
        loading="lazy"
      />
      <div v-else class="w-full h-full bg-gray-100 flex items-center justify-center">
        <i class="pi pi-image text-4xl text-gray-400"></i>
      </div>
    </div>
    
    <!-- Content below image -->
    <div class="p-4 flex flex-col flex-grow">
      <h3 class="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">{{ item.name }}</h3>
      <div class="flex justify-between items-center mt-auto">
        <p class="text-[#ff6f00] font-bold">${{ item.hourly_rate }}/hr</p>
        <span class="text-sm text-gray-500">{{ item.category }}</span>
      </div>
      <button 
        @click.stop="$emit('click')"
        class="mt-4 w-full bg-[#ff6f00] text-white py-2 rounded-lg hover:bg-[#ff9e00] transition-colors"
      >
        {{ item.is_featured ? 'Rent Now' : 'View Details' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
});

const getFullImageUrl = (imagePath) => {
  if (!imagePath) return null;
  return imagePath.startsWith('http') ? imagePath : `${import.meta.env.VITE_API_BASE_URL}${imagePath}`;
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Ensure consistent height for all cards */
.h-full {
  height: 100%;
}

/* Fixed height for image container */
.h-48 {
  height: 12rem; /* 192px */
}

/* Make sure buttons align at the bottom */
.flex-grow {
  flex-grow: 1;
}
</style>