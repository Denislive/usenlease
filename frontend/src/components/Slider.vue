<script setup>
import { ref, onMounted } from 'vue';
import Cta from '@/components/Cta.vue'

const currentSlide = ref(0);
const slides = [1, 2, 3]; // Add as many slides as you want

// Automatically go to the next slide every 5 seconds
onMounted(() => {
  setInterval(() => {
    nextSlide();
  }, 5000);
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
                    <div class="flex transition-transform duration-500 ease-in-out"
                        :style="`transform: translateX(-${currentSlide * 100}%)`">
                        <!-- Slide 1 -->
                        <div class="flex-shrink-0 w-full">
                            <img class="w-full h-48 object-cover" src="../assets/gifs/1.gif"
                                alt="Slide 1">
                        </div>
                        <!-- Slide 2 -->
                        <div class="flex-shrink-0 w-full">
                            <img class="w-full h-48 object-cover" src="../assets/gifs/2.gif"
                                alt="Slide 2">
                        </div>
                        <!-- Slide 3 -->
                        <div class="flex-shrink-0 w-full">
                            <img class="w-full h-48 object-cover" src="../assets/gifs/3.gif"
                                alt="Slide 3">
                        </div>
                    </div>
                </div>

                <!-- Navigation Buttons -->
                <i @click="prevSlide"
                    class="pi pi-arrow-circle-left absolute top-1/2 left-0 transform -translate-y-1/2 text-white p-2 rounded-full cursor-pointer bg-gray-800 hover:text-[#ffc107]"></i>
                <i @click="nextSlide"
                    class="pi pi-arrow-circle-right absolute top-1/2 right-0 transform -translate-y-1/2 text-white p-2 rounded-full cursor-pointer bg-gray-800 hover:text-[#ffc107]"></i>
            </div>

            <!-- Square Button Section (4 columns) -->
            <!-- <div class="col-span-4 flex items-center justify-end h-48 mr-4"> 
                <Cta />
            </div> -->
        </div>
    </div>
</template>

<style scoped>
/* Optional: Add additional styles if needed */
</style>
