<template>
    <div class="md:hidden">
      <button @click="toggleFilters" class="w-full text-xl font-bold mb-4 flex items-center">
        <i class="pi pi-filter mr-2"></i> Filters
      </button>
      <div v-if="showFilters" class="border border-gray-300 rounded-lg p-4 mb-4">
        <ul class="space-y-4">
          <!-- Category Filter -->
          <li class="product-filters-tab">
            <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Category</a>
            <ul class="ml-4 space-y-2">
              <li>
                <a href="#" class="text-xl text-gray-500" id="category-clear-all">Clear All</a>
              </li>
              <li><input id="category-checkbox1" type="checkbox" class="mr-2"><label for="category-checkbox1" class="text-xl">Category 1</label></li>
              <li><input id="category-checkbox2" type="checkbox" class="mr-2"><label for="category-checkbox2" class="text-xl">Category 2</label></li>
              <li><input id="category-checkbox3" type="checkbox" class="mr-2"><label for="category-checkbox3" class="text-xl">Category 3</label></li>
              <li><input id="category-checkbox4" type="checkbox" class="mr-2"><label for="category-checkbox4" class="text-xl">Category 4</label></li>
              <li><input id="category-checkbox5" type="checkbox" class="mr-2"><label for="category-checkbox5" class="text-xl">Category 5</label></li>
              <li><input id="category-checkbox6" type="checkbox" class="mr-2"><label for="category-checkbox6" class="text-xl">Category 6</label></li>
            </ul>
          </li>
  
          <!-- Size Filter -->
          <li class="product-filters-tab">
            <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Size</a>
            <ul class="ml-4 space-y-2">
              <li>
                <a href="#" class="text-xl text-gray-500" id="size-clear-all">Clear All</a>
              </li>
              <li><input id="size-checkbox1" type="checkbox" class="mr-2"><label for="size-checkbox1" class="text-xl">Small</label></li>
              <li><input id="size-checkbox2" type="checkbox" class="mr-2"><label for="size-checkbox2" class="text-xl">Medium</label></li>
              <li><input id="size-checkbox3" type="checkbox" class="mr-2"><label for="size-checkbox3" class="text-xl">Large</label></li>
              <li><input id="size-checkbox4" type="checkbox" class="mr-2"><label for="size-checkbox4" class="text-xl">X-Large</label></li>
              <li><input id="size-checkbox5" type="checkbox" class="mr-2"><label for="size-checkbox5" class="text-xl">XX-Large</label></li>
            </ul>
          </li>
  
          <!-- Color Filter -->
          <li class="product-filters-tab">
            <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Color</a>
            <ul class="ml-4 space-y-2">
              <li>
                <a href="#" class="text-xl text-gray-500" id="color-clear-all">Clear All</a>
              </li>
              <li><input id="color-checkbox1" type="checkbox" class="mr-2"><label for="color-checkbox1" class="text-xl">All Color</label></li>
              <li><input id="color-checkbox2" type="checkbox" class="mr-2"><label for="color-checkbox2" class="text-xl">Black</label></li>
              <li><input id="color-checkbox3" type="checkbox" class="mr-2"><label for="color-checkbox3" class="text-xl">White</label></li>
              <li><input id="color-checkbox4" type="checkbox" class="mr-2"><label for="color-checkbox4" class="text-xl">Grey</label></li>
              <li><input id="color-checkbox5" type="checkbox" class="mr-2"><label for="color-checkbox5" class="text-xl">Red</label></li>
              <li><input id="color-checkbox6" type="checkbox" class="mr-2"><label for="color-checkbox6" class="text-xl">Blue</label></li>
              <li><input id="color-checkbox7" type="checkbox" class="mr-2"><label for="color-checkbox7" class="text-xl">Green</label></li>
              <li><input id="color-checkbox8" type="checkbox" class="mr-2"><label for="color-checkbox8" class="text-xl">Purple</label></li>
              <li><input id="color-checkbox9" type="checkbox" class="mr-2"><label for="color-checkbox9" class="text-xl">Multi-color</label></li>
            </ul>
          </li>
  
          <!-- Price Filter -->
          <li class="product-filters-tab">
            <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Price</a>
            <ul class="ml-4 space-y-2">
              <li>
                <a href="#" class="text-xl text-gray-500" id="price-clear-all">Clear All</a>
              </li>
              <li><input id="price-checkbox1" type="checkbox" class="mr-2"><label for="price-checkbox1" class="text-xl">Under $25</label></li>
              <li><input id="price-checkbox2" type="checkbox" class="mr-2"><label for="price-checkbox2" class="text-xl">$25–$50</label></li>
              <li><input id="price-checkbox3" type="checkbox" class="mr-2"><label for="price-checkbox3" class="text-xl">$50–$250</label></li>
              <li><input id="price-checkbox4" type="checkbox" class="mr-2"><label for="price-checkbox4" class="text-xl">$250–$600</label></li>
              <li><input id="price-checkbox5" type="checkbox" class="mr-2"><label for="price-checkbox5" class="text-xl">$600–$1,000</label></li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  
    <!-- Desktop View -->
    <div class="hidden md:block">
      <h1 class="text-xl font-bold mb-4">
        <i class="pi pi-filter"></i> Filters
      </h1>
      <ul class="space-y-4">
        <!-- Category Filter -->
        <li class="product-filters-tab">
          <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Category</a>
          <ul class="ml-4 space-y-2">
            <li>
              <a href="#" class="text-xl text-gray-500" id="category-clear-all">Clear All</a>
            </li>
            <li><input id="category-checkbox1" type="checkbox" class="mr-2"><label for="category-checkbox1" class="text-xl">Category 1</label></li>
            <li><input id="category-checkbox2" type="checkbox" class="mr-2"><label for="category-checkbox2" class="text-xl">Category 2</label></li>
            <li><input id="category-checkbox3" type="checkbox" class="mr-2"><label for="category-checkbox3" class="text-xl">Category 3</label></li>
            <li><input id="category-checkbox4" type="checkbox" class="mr-2"><label for="category-checkbox4" class="text-xl">Category 4</label></li>
            <li><input id="category-checkbox5" type="checkbox" class="mr-2"><label for="category-checkbox5" class="text-xl">Category 5</label></li>
            <li><input id="category-checkbox6" type="checkbox" class="mr-2"><label for="category-checkbox6" class="text-xl">Category 6</label></li>
          </ul>
        </li>
  
        <!-- Size Filter -->
        <li class="product-filters-tab">
          <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Size</a>
          <ul class="ml-4 space-y-2">
            <li>
              <a href="#" class="text-xl text-gray-500" id="size-clear-all">Clear All</a>
            </li>
            <li><input id="size-checkbox1" type="checkbox" class="mr-2"><label for="size-checkbox1" class="text-xl">Small</label></li>
            <li><input id="size-checkbox2" type="checkbox" class="mr-2"><label for="size-checkbox2" class="text-xl">Medium</label></li>
            <li><input id="size-checkbox3" type="checkbox" class="mr-2"><label for="size-checkbox3" class="text-xl">Large</label></li>
            <li><input id="size-checkbox4" type="checkbox" class="mr-2"><label for="size-checkbox4" class="text-xl">X-Large</label></li>
            <li><input id="size-checkbox5" type="checkbox" class="mr-2"><label for="size-checkbox5" class="text-xl">XX-Large</label></li>
          </ul>
        </li>
  
        <!-- Color Filter -->
        <li class="product-filters-tab">
          <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Color</a>
          <ul class="ml-4 space-y-2">
            <li>
              <a href="#" class="text-xl text-gray-500" id="color-clear-all">Clear All</a>
            </li>
            <li><input id="color-checkbox1" type="checkbox" class="mr-2"><label for="color-checkbox1" class="text-xl">All Color</label></li>
            <li><input id="color-checkbox2" type="checkbox" class="mr-2"><label for="color-checkbox2" class="text-xl">Black</label></li>
            <li><input id="color-checkbox3" type="checkbox" class="mr-2"><label for="color-checkbox3" class="text-xl">White</label></li>
            <li><input id="color-checkbox4" type="checkbox" class="mr-2"><label for="color-checkbox4" class="text-xl">Grey</label></li>
            <li><input id="color-checkbox5" type="checkbox" class="mr-2"><label for="color-checkbox5" class="text-xl">Red</label></li>
            <li><input id="color-checkbox6" type="checkbox" class="mr-2"><label for="color-checkbox6" class="text-xl">Blue</label></li>
            <li><input id="color-checkbox7" type="checkbox" class="mr-2"><label for="color-checkbox7" class="text-xl">Green</label></li>
            <li><input id="color-checkbox8" type="checkbox" class="mr-2"><label for="color-checkbox8" class="text-xl">Purple</label></li>
            <li><input id="color-checkbox9" type="checkbox" class="mr-2"><label for="color-checkbox9" class="text-xl">Multi-color</label></li>
          </ul>
        </li>
  
        <!-- Price Filter -->
        <li class="product-filters-tab">
          <a href="#" class="text-lg font-semibold hover:text-[#1c1c1c]">Price</a>
          <ul class="ml-4 space-y-2">
            <li>
              <a href="#" class="text-xl text-gray-500" id="price-clear-all">Clear All</a>
            </li>
            <li><input id="price-checkbox1" type="checkbox" class="mr-2"><label for="price-checkbox1" class="text-xl">Under $25</label></li>
            <li><input id="price-checkbox2" type="checkbox" class="mr-2"><label for="price-checkbox2" class="text-xl">$25–$50</label></li>
            <li><input id="price-checkbox3" type="checkbox" class="mr-2"><label for="price-checkbox3" class="text-xl">$50–$250</label></li>
            <li><input id="price-checkbox4" type="checkbox" class="mr-2"><label for="price-checkbox4" class="text-xl">$250–$600</label></li>
            <li><input id="price-checkbox5" type="checkbox" class="mr-2"><label for="price-checkbox5" class="text-xl">$600–$1,000</label></li>
          </ul>
        </li>
      </ul>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const showFilters = ref(false);
  
  const toggleFilters = () => {
      showFilters.value = !showFilters.value;
  };
  </script>
  
  <style scoped>
  /* Filter styles can go here if needed */
  .product-filters-tab a {
      color: #1c1c1c; /* Color for links */
      transition: color 0.3s ease; /* Smooth transition for hover */
  }
  
  .product-filters-tab a:hover {
      color: #1c1c1c; /* Change text color on hover */
  }
  
  input[type="checkbox"] {
      accent-color: #ffc107; /* Custom color for checkboxes */
  }
  
  /* Overall Filter Menu */
  ul {
      list-style: none; /* Remove bullet points */
      padding-left: 0; /* Remove default padding */
  }
  </style>