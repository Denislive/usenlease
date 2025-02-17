<template>
  <div class="bg-[#1c1c1c] p-1 sticky top-0 z-50">
    <div class="w-11/12 md:w-5/6 lg:w-5/6 xl:w-6/6 mx-auto">
      <header class="text-white flex justify-between items-center">
        <!-- Logo -->
        <RouterLink :to="{ name: 'home' }" class="flex items-center">
          <img :src="company.companyInfo?.logo" :alt="company.companyInfo?.logo" class="h-16" />
        </RouterLink>

        <!-- Role Switch -->
        <div v-if="authStore.isAuthenticated"
          class="flex items-center justify-between bg-[#121212] border border-gray-700 p-4 rounded-lg shadow-md hidden md:block">
          <div class="flex items-center space-x-3">
            <span class="text-sm text-gray-300">Switch to {{ authStore.user?.role === 'lessor' ? 'lessee' : 'lessor'
              }}:</span>
            <label for="role-toggle" class="inline-flex relative items-center cursor-pointer">
              <input type="checkbox" id="role-toggle" v-model="authStore.isOn" class="sr-only peer"
                @change="authStore.updateUserRole()" />
              <div
                class="w-11 h-6 bg-gray-700 border border-gray-500 rounded-full peer-checked:bg-[#ffc107] peer-checked:after:translate-x-5 after:content-[''] after:absolute after:left-0.5 after:top-0.5 after:w-5 after:h-5 after:rounded-full after:bg-gray-300 after:shadow-lg transition-all">
              </div>
            </label>
          </div>
        </div>


        <!-- Authenticated User Menu -->
        <div v-if="authStore.isAuthenticated" class="flex items-center space-x-4">
          <!-- Browse Items Button for Lessee -->
          <RouterLink :to="{ name: 'categories' }">
            <a
              class="px-4 py-2 bg-gradient-to-r from-[#ff6f00] to-[#ffc107] text-white font-semibold rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Browse Items
            </a>
          </RouterLink>

          <!-- Lease Out Button for Lessor -->
          <RouterLink v-if="authStore.user.role === 'lessor'" :to="{ name: 'list-item' }">
            <a
              class="px-4 py-2 bg-[#ffc107] text-[#1c1c1c] hidden md:block rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Lease Out
            </a>
          </RouterLink>

          <!-- Equipment Icon -->
          <div v-if="authStore.user.role === 'lessor'" class="relative">
            <RouterLink to="/profile?section=my-equipments" class="flex items-center relative">
              <i class="pi pi-bars text-3xl mx-2"></i>
              <span
                class="absolute -top-1 -right-0 bg-red-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                {{ store.userEquipments.length }}
              </span>
            </RouterLink>
          </div>


          <!-- Cart Icon -->
          <div v-if="authStore.user.role === 'lessee'" class="relative">
            <RouterLink to="/cart" class="flex items-center relative">
              <i class="pi pi-shopping-cart text-4xl mx-2"></i>
              <span
                class="absolute -top-1 -right-2 bg-red-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                {{ cartStore.cart.length }}
              </span>
            </RouterLink>
          </div>


          <!-- Profile Icon with Dropdown for Profile & Logout -->
          <div class="relative hidden lg:block" @mouseenter="showDropdownWithDelay(true)"
            @mouseleave="showDropdownWithDelay(false)">
            <button class="hidden md:flex items-center space-x-2 focus:outline-none">
              <img :src="`${authStore.user.image}`" alt="Profile Icon"
                class="w-10 h-10 rounded-full border border-gray-300" />
            </button>
            <div
              class="absolute left-1/2 mt-7 w-32 bg-[#1c1c1c] rounded-lg shadow-lg text-center z-10 transform -translate-x-1/2"
              v-show="showDropdown">
              <RouterLink to="/profile" @click="showDropdown = false"
                class="block py-2 text-white hover:text-[#ffc107]">
                Profile
              </RouterLink>
              <button @click="handleLogout" class="w-full px-4 py-2 text-white hover:bg-red-500 hover:text-[#1c1c1c]">
                Logout
              </button>
            </div>
          </div>
        </div>

        <!-- Not Authenticated User Menu -->
        <div v-else class="flex items-center space-x-4">
          <!-- Browse Items Button for Non-Authenticated Users -->
          <RouterLink :to="{ name: 'categories' }">
            <a
              class="hidden lg:block px-6 py-2 bg-gradient-to-r from-[#ff6f00] to-[#ffc107] text-white font-semibold rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Browse Items
            </a>
          </RouterLink>

          <!-- Login Button -->
          <RouterLink to="/login" class="text-white">
            <button
              class="px-6 py-2 hidden md:block text-white font-semibold rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Login
            </button>
          </RouterLink>

          <!-- Lease Out Button for Non-Authenticated Users -->
          <RouterLink :to="{ name: 'list-item' }">
            <a
              class="px-6 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Lease Out
            </a>
          </RouterLink>

          <!-- Cart Icon -->
          <div class="relative">
            <RouterLink to="/cart" class="flex items-center relative">
              <i class="pi pi-shopping-cart text-4xl mx-2"></i>
              <span
                class="absolute -top-1 -right-2 bg-red-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                {{ cartStore.cart.length }}
              </span>
            </RouterLink>
          </div>

        </div>
      </header>
    </div>
  </div>

  <!-- Sticky Navbar for Mobile -->
  <nav class="fixed bottom-0 left-0 right-0 bg-[#1c1c1c] text-white p-2 shadow-lg md:hidden z-10">
    <div class="flex justify-around items-center">
      <div class="text-center">
        <RouterLink to="/" class="flex flex-col items-center">
          <i class="pi pi-home text-xl"></i>
          <small>Home</small>
        </RouterLink>
      </div>

      <!-- Conditional Links for Authenticated Users -->
      <div v-if="authStore.isAuthenticated">
        <div v-if="authStore.user.role === 'lessor'" class="text-center">
          <RouterLink to="/list-item" class="flex flex-col items-center">
            <i class="pi pi-plus text-xl"></i>
            <small>List</small>
          </RouterLink>
        </div>
        <div v-if="authStore.user.role === 'lessee'" class="text-center">
          <RouterLink to="/categories" class="flex flex-col items-center">
            <i class="pi pi-search text-xl"></i>
            <small>Browse</small>
          </RouterLink>
        </div>
      </div>

      <!-- Links for Unauthenticated Users -->
      <div v-else>
        <div class="text-center">
          <RouterLink to="/profile?section=reports" class="flex flex-col items-center">
            <i class="pi pi-bookmark text-xl"></i>
            <small>Reports</small>
          </RouterLink>
        </div>
      </div>

      <!-- Other Links -->
      <div class="text-center">
        <RouterLink to="/profile?section=chats" class="flex flex-col items-center">
          <i class="pi pi-comments text-xl"></i>
          <small>Messages</small>
        </RouterLink>
      </div>
      <div class="text-center">
        <RouterLink to="/profile" class="flex flex-col items-center">
          <i class="pi pi-user text-xl"></i>
          <small>Profile</small>
        </RouterLink>
      </div>
    </div>
  </nav>
</template>



<script setup>
import { ref, computed, onMounted } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth'; // Import the auth store
import { useCartStore } from '@/store/cart'; // Adjust the path as necessary
import axios from 'axios';
import Cookies from 'js-cookie';

import { useCompanyInfoStore } from '@/store/company';
import useNotifications from '@/store/notification';
import { useEquipmentsStore } from '@/store/equipments';

const api_base_url = import.meta.env.VITE_API_BASE_URL;

const company = useCompanyInfoStore();
const cartStore = useCartStore();
const store = useEquipmentsStore();

const { showNotification } = useNotifications();

const showDropdown = ref(false);
const authStore = useAuthStore();
const router = useRouter();
const user = ref({
  user_address: {
    full_name: '',
    street_address: '',
    city: '',
    state: '',
    zip_code: '',
    country: '',
  },
});

let dropdownTimeout;

const showDropdownWithDelay = (show) => {
  clearTimeout(dropdownTimeout);
  if (show) {
    dropdownTimeout = setTimeout(() => {
      showDropdown.value = true;
    }, 50); // Delay for showing the dropdown
  } else {
    dropdownTimeout = setTimeout(() => {
      showDropdown.value = false;
    }, 200); // Delay for hiding the dropdown
  }
};



onMounted(async () => {
  if (authStore.isAuthenticated) {
    await authStore.getUserData(); // Fetch user data after login
    user.value = authStore.user;
    await store.fetchUserEquipments();
  }
  await company.fetchCompanyInfo(); // Load company information
});

// Handle logout functionality
const handleLogout = async () => {
  try {
    await authStore.logout(); // Perform logout
    router.push('/'); // Redirect to the homepage
  } catch (error) {
    console.error('Error during logout:', error);
    showNotification('error', 'Error during logout. Please try again.', 'error');
  }
};
</script>

<style scoped>
/* Optional additional styles can go here */
</style>
