<script setup>
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import Footbar from '@/components/Footbar.vue'

</script>

<template>
    <Navbar />
    
    <RouterView />
    <Footbar />
</template>

<style scoped>

</style>
