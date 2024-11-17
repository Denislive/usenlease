<template>
    <!-- Breadcrumb Navigation -->
    <div class="md:block">
      <div class="mx-auto">
        <nav aria-label="Breadcrumb" class="text-center">
          <ul class="flex justify-center space-x-4 text-gray-700">
            <!-- If 'current' is defined, render the two links for category and subcategory -->
            <li v-if="current" class="text-gray-800">
              <RouterLink
                :to="{ name: 'category-details', query: { cat: category } }"
                class="hover:text-[#ffc107] mx-6"
              >
                {{ category }}
              </RouterLink>
  
              <RouterLink
                :to="{ name: 'category-details', query: { cat: current} }"
                class="hover:text-[#ffc107]"
              >
                {{ current }}
              </RouterLink>
            </li>
  
            <!-- If 'current' is not defined, just display the category -->
            <li v-else class="text-gray-800">
              <RouterLink href="#" class="hover:text-[#ffc107]">
                {{ category }}
              </RouterLink>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </template>
  
  <script>
  import { RouterLink, useRoute } from 'vue-router';
  
  export default {
    setup() {
      const route = useRoute();
      const category = route.query.cat; // Extract the 'cat' query parameter
      const current = route.query.sub; // Extract the 'sub' query parameter if exists
  
      return {
        category,
        current,
      };
    },
  };
  </script>
  
  <style scoped>
  /* Additional styles can go here if needed */
  </style>
  