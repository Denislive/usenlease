<script setup>
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import Footbar from '@/components/Footbar.vue'
import Notification from '@/components/Notification.vue';



</script>

<template>
    <Navbar />
    <Notification />
    
    <RouterView />
    <Footbar />
</template>

<style scoped>

</style>
