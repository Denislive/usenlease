<template>
  <div class="bg-white rounded-xl shadow-md overflow-hidden transition-all hover:shadow-lg cursor-pointer flex flex-col h-full">
    <!-- Image container with aspect ratio box -->
    <div class="relative w-full aspect-[4/3] overflow-hidden bg-gray-100">
      <img 
        v-if="item.images?.length > 0"
        :src="getFullImageUrl(item.images[0].image_url)" 
        :alt="`Image of ${item.name}`"
        class="absolute inset-0 w-full h-full object-contain p-2"
        loading="lazy"
        @error="handleImageError"
      />
      <div v-else class="absolute inset-0 flex items-center justify-center">
        <i class="pi pi-image text-4xl text-gray-400"></i>
      </div>
    </div>
    
    <!-- Content below image -->
    <div class="p-4 flex flex-col flex-grow">
      <h3 class="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">{{ item.name }}</h3>
      <div class="flex justify-between items-center mt-auto">
        <p class="text-[#ff6f00] font-bold">${{ item.hourly_rate }}/hr</p>
        <div class="flex items-center mb-2">
              <span class="rating text-yellow-500 mr-1 text-xs sm:text-sm">{{ renderStars(item.rating) }}</span>
              <span class="reviews text-gray-600 text-[10px] sm:text-xs">
                ({{ item.equipment_reviews?.length || 0 }})
              </span>
            </div>
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

const handleImageError = (e) => {
  e.target.src = '/placeholder-image.jpg';
  e.target.classList.replace('object-contain', 'object-cover');
};

const renderStars = (rating) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  return '★'.repeat(fullStars) + (halfStar ? '☆' : '') + '☆'.repeat(5 - fullStars - halfStar);
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Aspect ratio box */
.aspect-\[4\/3\] {
  position: relative;
  padding-bottom: 75%; /* 4:3 aspect ratio */
}

.aspect-\[4\/3\] > * {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* Make sure buttons align at the bottom */
.flex-grow {
  flex-grow: 1;
}

/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* Hover effects */
.hover\:shadow-lg:hover {
  --tw-shadow: 0 10px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --tw-shadow-colored: 0 10px 25px -5px var(--tw-shadow-color), 0 8px 10px -6px var(--tw-shadow-color);
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}
</style>