<script setup>
import Hero from '@/components/Hero.vue';
import Addresses from '@/components/Addresses.vue';
import CheckoutSummary from '@/components/CheckoutSummary.vue';

</script>

<template>
  <div>
    <Hero />
  </div>

  <div class="mx-auto p-2 w-6/8 sm:w-11/12">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-4 p-1">
    
      <!-- Main Content Section -->
      <main class="md:col-span-6 bg-gray-100 p-1">
        <CheckoutSummary />
      </main>
      <!-- Sidebar Section -->
      <aside class="md:col-span-6 bg-gray-100 rounded p-2">
        <Addresses />
      </aside>
    </div>
    <EquipmentTabs />

  </div>

</template>

<style scoped>
/* Add any specific styles for the Categories page here */
</style>