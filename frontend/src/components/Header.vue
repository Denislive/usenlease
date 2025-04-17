<template>
    <header class="sticky top-0 z-50 bg-white shadow p-4 flex justify-between items-center">
        <button @click="toggleSidebar" class="md:hidden">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
        </button>
        <h1 class="text-xl font-semibold">{{ currentRouteName }}</h1>
        <div class="flex items-center space-x-4">
            <span>{{ authStore.user ? `Welcome, ${authStore.user.first_name}` : 'Welcome back' }}</span>
            <button v-if="authStore.user" @click="logout" class="text-red-500">
                Logout
            </button>
        </div>
    </header>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const currentRouteName = computed(() => {
    return route.matched.find((r) => r.name)?.name || 'Dashboard';
});

const toggleSidebar = () => {
    const event = new CustomEvent('toggle-sidebar');
    window.dispatchEvent(event);
};

const logout = () => {
    authStore.logout();
    router.push('/login');
};
</script>