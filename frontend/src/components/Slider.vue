<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Cta from '@/components/Cta.vue';

// Reactive variables
const currentSlide = ref(0);
const slides = [
  import.meta.glob('@/assets/gifs/*.gif') // Automatically load GIFs
];

let intervalId = null;

// Automatically go to the next slide every 10 seconds
onMounted(() => {
  intervalId = setInterval(nextSlide, 10000);
});

// Cleanup interval when component is unmounted
onUnmounted(() => {
  clearInterval(intervalId);
});

const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % slides.length;
};

const prevSlide = () => {
  currentSlide.value = (currentSlide.value - 1 + slides.length) % slides.length;
};
</script>

<template>
  <div class="container mx-auto p-4">
    <div class="grid grid-cols-12 gap-4">
      <!-- Carousel Section (8 columns) -->
      <div class="col-span-12 relative" role="region" aria-label="Equipment Slider">
        <div class="overflow-hidden rounded-lg">
          <div
            class="flex transition-transform duration-500 ease-in-out"
            :style="`transform: translateX(-${currentSlide * 100}%)`"
          >
            <div v-for="(slide, index) in slides" :key="index" class="flex-shrink-0 w-full">
              <img class="w-full h-72 object-cover" :src="slide" :alt="`Slide ${index + 1}`" />
            </div>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <i
          @click="prevSlide"
          class="pi pi-arrow-circle-left absolute top-1/2 left-0 transform -translate-y-1/2 text-white p-2 rounded-full cursor-pointer bg-gray-800 hover:text-[#ffc107]"
        ></i>
        <i
          @click="nextSlide"
          class="pi pi-arrow-circle-right absolute top-1/2 right-0 transform -translate-y-1/2 text-white p-2 rounded-full cursor-pointer bg-gray-800 hover:text-[#ffc107]"
        ></i>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Optional: Add additional styles if needed */
</style>
