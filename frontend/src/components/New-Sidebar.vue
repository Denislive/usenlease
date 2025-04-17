<template>
    <div
      :class="[
        'bg-[#1c1c1c] text-white w-64 space-y-6 py-40 md:py-7 px-2 absolute inset-y-0 left-0 transform',
        isOpen ? 'translate-x-0' : '-translate-x-full',
        'md:relative md:translate-x-0 transition duration-300 ease-in-out z-40',
      ]"
    >
      <div class="flex items-center justify-between px-4">
        <h2 class="text-2xl font-semibold text-[#ffc107]">Dashboard</h2>
        <button @click="toggleSidebar" class="md:hidden">
          <i class="pi pi-times text-xl"></i>
        </button>
      </div>
  
      <nav class="px-2">
        <router-link
          v-for="item in menuItems"
          :key="item.name"
          :to="item.path"
          @click="handleNavigation"
          class="flex items-center gap-3 py-2.5 px-4 rounded transition duration-200 hover:bg-[#333333]"
          :class="{ 'bg-[#333333] text-[#ffc107] font-semibold': $route.path === item.path }"
        >
          <i :class="['pi', item.icon, 'text-[#ffc107]']" />
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue';
  
  const isOpen = ref(false);
  
  const menuItems = [
    { name: 'My Account', path: '/new-profile/account', icon: 'pi-user' },
    { name: 'Orders', path: '/new-profile/orders', icon: 'pi-shopping-cart' },
    { name: 'Items', path: '/new-profile/items', icon: 'pi-box' },
    { name: 'Chats', path: '/new-profile/chats', icon: 'pi-comments' },
    { name: 'Statistics', path: '/new-profile/statistics', icon: 'pi-chart-bar' },
    { name: 'Settings', path: '/new-profile/settings', icon: 'pi-cog' },
  ];
  
  const toggleSidebar = () => {
    isOpen.value = !isOpen.value;
  };
  
  const handleToggle = () => {
    isOpen.value = !isOpen.value;
  };
  
  const handleNavigation = () => {
    if (window.innerWidth < 768) {
      isOpen.value = false;
    }
  };
  
  onMounted(() => {
    window.addEventListener('toggle-sidebar', handleToggle);
  });
  
  onUnmounted(() => {
    window.removeEventListener('toggle-sidebar', handleToggle);
  });
  </script>
  
  <style scoped>
  /* Optional: Smooth icon hover */
  .pi {
    transition: color 0.2s ease;
  }
  </style>
  