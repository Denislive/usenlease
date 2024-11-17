<template>
    <div class="empty-list-container text-center py-16">
        <i class="pi pi-exclamation-circle text-9xl text-gray-500"></i>
      <p class="text-xl text-gray-500 mt-4">Oops! Nothing matched your query!</p>
      <p class="text-xl text-gray-500 mt-4">Try other tags and keywords for the item.</p>

    </div>
  </template>
  
  <script setup>
  // No props needed, this is a simple empty state component.
  </script>
  
  <style scoped>
  .empty-list-container {
    max-width: 400px;
    margin: 0 auto;
  }
  </style>
  