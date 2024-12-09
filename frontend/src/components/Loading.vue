<template>
    <div class="flex items-center justify-center h-screen bg-gray-900">
      <div class="loading-container">
        <div class="loading-circle"></div>
        <div class="loading-circle"></div>
        <div class="loading-circle"></div>
      </div>
    </div>
  </template>
  
  <script setup>
  // No JavaScript needed for this simple, CSS-based animation.
  </script>
  
  <style scoped>
  /* Centering the loading component */
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
  