<template>
    <div class="flex h-screen bg-gray-100">
        <!-- Sidebar -->
        <NewSidebar />
        <!-- Main Content -->
        <div class="flex-1 flex flex-col">
            <Header />
            <main class="flex-1 p-6 overflow-x-auto bg-white">
                <router-view /> <!-- Renders Account, Orders, etc. -->
            </main>
        </div>
    </div>
</template>

<script setup>
import Header from '@/components/Header.vue';
import NewSidebar from '@/components/New-Sidebar.vue';
</script>