<template>
<section class="hero bg-gradient-to-r from-[#ff9e00] to-[#ffc107] py-4 relative text-white overflow-hidden">
  <!-- Background Elements -->
  <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-60"></div>

  <!-- Hero Content -->
  <div class="container mx-auto text-center relative z-10">
    <h1 class="text-4xl sm:text-5xl font-bold leading-tight mb-6 animate__animated animate__fadeIn animate__delay-1s">
      Rent the Best Equipment for Your Needs
    </h1>
    <p class="text-lg sm:text-xl mb-8 animate__animated animate__fadeIn animate__delay-2s">
      Find top-quality equipment for any project. Fast delivery and great customer support.
    </p>
    
    <!-- Location Button -->
    <div class="flex justify-center mb-6">
      <div class="flex items-center cursor-pointer relative group">
        <button
          class="bg-[#1c1c1c] text-dark py-3 px-8 rounded-full text-lg font-semibold hover:bg-[#ff9e00] transition duration-300 transform hover:scale-105 group-hover:animate-pulse"
          id="locationButton"
        >
          All in USA
        </button>
        <div class="absolute top-0 left-0 w-full h-full bg-[#ff9e00] opacity-0 group-hover:opacity-20 transition-all duration-300"></div>
      </div>
    </div>

    <!-- Search Box -->
    <div class="flex justify-center mb-8">
      <div class="sm:w-3/4 lg:w-1/2 relative">
        <div class="flex items-center bg-white p-3 rounded-full shadow-lg transform transition-all hover:scale-105">
          <input
            type="text"
            class="flex-1 text-[#1c1c1c] border-none p-3 text-lg focus:outline-none rounded-l-full"
            placeholder="Search for equipment..."
            v-model="searchQuery"
            @input="updateSearch"
          />
          <button class="bg-[#ff6f00] text-white rounded-r-full px-6 py-3 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110">
            <i class="pi pi-search text-lg"></i>
          </button>
        </div>
        <!-- Floating Search Icon -->
        <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 animate-bounce">
          🔍
        </div>
      </div>
    </div>

  </div>

  <!-- Decorative Circle Effect -->
  <div class="absolute top-1/4 left-1/4 w-24 h-24 bg-[#ff6f00] rounded-full opacity-20 animate-pulse"></div>
  <div class="absolute top-2/3 right-1/4 w-36 h-36 bg-[#ff6f00] rounded-full opacity-30 animate-pulse"></div>
</section>



</template>

<script setup>
import { computed } from 'vue';
import { useStore } from 'vuex';

const store = useStore();
const searchQuery = computed({
  get: () => store.getters.getSearchQuery,
  set: (value) => {
    store.dispatch('setSearchQuery', value);
  },
});

// The updateSearch function is no longer needed since we're using computed setter
</script>

<style scoped>
/* Additional styles can go here if needed */
</style>
