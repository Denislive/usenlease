<template>
    <RouterLink  :to="{ name: 'list-item' }"
        class="flex flex-col items-center justify-center w-48 h-48 bg-[#1c1c1c] text-white rounded-lg shadow hover:text-[#ffc107] transition duration-300">
        <div class="icon-container mb-2">
            <i class="pi pi-plus-circle text-4xl"></i>
        </div>
        <span class="main-text text-lg font-semibold">Equipment</span>
    </RouterLink> </template>

<script>
import { RouterLink } from 'vue-router';


</script>

<style scoped>
/* Additional styles can go here if needed */
</style>