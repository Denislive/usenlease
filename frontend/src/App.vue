<script setup>
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import Footbar from '@/components/Footbar.vue'
import Notification from '@/components/Notification.vue'

import { ref } from 'vue'

// This state will control whether the loading indicator is visible or not
const isLoading = ref(false)

// You can replace this with real logic to set isLoading to false
// For example, after fetching data or completing an API request:
// Example:
// fetchData().then(() => {
//   isLoading.value = false;
// });
</script>

<template>
  <Navbar />
  <Notification />
  
  <!-- Conditional rendering of the Loading component -->
  <div v-if="isLoading" class="loading-wrapper">
    <div class="loading-container">
      <div class="loading-circle"></div>
      <div class="loading-circle"></div>
      <div class="loading-circle"></div>
    </div>
  </div>

  <RouterView />
  <Footbar />
</template>

<style scoped>
/* Centering the loading component */
.loading-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
}

/* Loading container */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

/* Individual loading circles */
.loading-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #ff9e00;
  animation: bounce 1.2s infinite ease-in-out;
}

/* Adding different delays for a smooth effect */
.loading-circle:nth-child(1) {
  animation-delay: 0s;
}
.loading-circle:nth-child(2) {
  animation-delay: 0.2s;
}
.loading-circle:nth-child(3) {
  animation-delay: 0.4s;
}

/* 3D Bounce Animation */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}
</style>
