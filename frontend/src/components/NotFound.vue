<template>
    <div class="flex flex-col items-center justify-center h-screen bg-gray-100 p-4">
      <div class="bg-white shadow-md rounded-lg p-8 text-center max-w-md">
        <i class="pi pi-exclamation-triangle text-6xl text-yellow-500 mb-4"></i>
        <h1 class="text-3xl font-bold text-gray-800">404 - Not Found</h1>
        <p class="text-gray-600 mt-2">
          Sorry, the page you are looking for does not exist.
        </p>
        <RouterLink
          to="/"
          class="mt-6 inline-block bg-[#1c1c1c] text-white py-2 px-4 rounded hover:bg-gray-800 transition duration-200"
        >
          Go to Home
        </RouterLink>
      </div>
    </div>
  </template>
  
  <script setup>
  // You can add any necessary script logic here if needed.
  </script>
  
  <style scoped>
  /* Optional additional styles can go here */
  </style>
  