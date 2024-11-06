<script setup>
import Hero from '@/components/Hero.vue'
import Sidebar from '@/components/Sidebar.vue'
import Slider from '@/components/Slider.vue'
import Equipment from '@/components/Equipment.vue'

import MobileCategories from '@/components/MobileCategories.vue'


</script>

<template>
  <Hero />


  <div class="container mx-auto py-2 w-5/6 hidden md:block">

    <div class="grid grid-cols-12 gap-4 p-1">
      <!-- Sidebar Section -->
      <aside class="col-span-3 bg-gray-100 rounded p-2  ">
        <Sidebar />
      </aside>
       
      <!-- Main Content Section -->
      <main class="col-span-9 bg-gray-100 p-1">
        <Slider />
        <Equipment />
      </main>
      
    </div>
  </div>
  <div class="container p-2 md:hidden">
    <MobileCategories />
  </div>


</template>
