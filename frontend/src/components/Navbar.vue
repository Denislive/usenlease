<template>
  <div class="bg-[#1c1c1c] p-1 sticky top-0 z-50">
    <div class="w-11/12 md:w-5/6 lg:w-5/6 xl:w-4/6 mx-auto">
      <header class="text-white flex justify-between items-center">

        <!-- Logo -->
        <RouterLink :to="{ name: 'home' }" class="flex items-center">
          <img src="@/assets/images/logo.jpeg" alt="Use N lease Logo" class="h-20" />
        </RouterLink>

        <!-- Authenticated User Menu -->
        <div v-if="authStore.isAuthenticated" class="flex items-center space-x-4">
          
          <!-- Browse Items Button for Lessee -->
          <RouterLink v-if="authStore.user.role === 'lessee'" :to="{ name: 'categories' }">
            <a
              class="px-6 py-2 bg-gradient-to-r from-[#ff6f00] to-[#ffc107] text-white font-semibold rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Browse Items
            </a>
          </RouterLink>

          <!-- Profile Icon with Dropdown for Profile & Logout -->
          <div class="relative" @mouseenter="showDropdownWithDelay(true)"
            @mouseleave="showDropdownWithDelay(false)">
            <button class="hidden md:flex items-center space-x-2 focus:outline-none">
              <img :src="`${api_base_url}${authStore.user.image}`" alt="Profile Icon"
                class="w-10 h-10 rounded-full border border-gray-300" />
            </button>
            <div
              class="absolute left-1/2 mt-7 w-32 bg-[#1c1c1c] rounded-lg shadow-lg text-center z-10 transform -translate-x-1/2"
              v-show="showDropdown">
              <RouterLink to="/profile" @click="showDropdown = false" class="block py-2 text-white hover:text-[#ffc107]">
                Profile
              </RouterLink>
              <button @click="handleLogout" class="w-full px-4 py-2 text-white hover:bg-red-500 hover:text-[#1c1c1c]">
                Logout
              </button>
            </div>

            

            
          </div>
           <!-- Lease Out Button for Lessor -->
           <RouterLink v-if="authStore.user.role === 'lessor'" :to="{ name: 'list-item' }">
            <a href="/browse"
              class="px-6 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Lease Out
            </a>
          </RouterLink>
          <!-- Cart Icon -->
          <div v-if="authStore.user.role === 'lessee'" class="relative">
            <RouterLink to="/cart" class="flex items-center">
              <i class="pi pi-shopping-cart text-4xl mx-4"></i>
              <span
                class="absolute top-[-15px] right-[-5px] bg-red-600 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">{{ cartStore.cart.length }}</span>
            </RouterLink>
          </div>

         

          
        </div>

        <!-- Not Authenticated User Menu -->
        <div v-else class="flex items-center space-x-4">
          <!-- Browse Items Button for Non-Authenticated Users -->
          <RouterLink :to="{ name: 'categories' }">
            <a
              class="px-6 py-2 bg-gradient-to-r from-[#ff6f00] to-[#ffc107] text-white font-semibold rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Browse Items
            </a>
          </RouterLink>
          
          <!-- Login Button -->
          <RouterLink to="/login" class="text-white">
            <button class="px-6 py-2  text-white font-semibold rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Login
            </button>
          </RouterLink>

          <!-- Lease Out Button for Non-Authenticated Users -->
          <RouterLink :to="{ name: 'list-item' }">
            <a href="/browse"
              class="px-6 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
              Lease Out
            </a>
          </RouterLink>

          <!-- Cart Icon -->
          <div class="relative">
            <RouterLink to="/cart" class="flex items-center">
              <i class="pi pi-shopping-cart text-4xl mx-4"></i>
              <span
                class="absolute top-[-15px] right-[-5px] bg-red-600 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">{{ cartStore.cart.length }}</span>
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
          <RouterLink to="/list" class="flex flex-col items-center">
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
import { ref, watchEffect, onMounted } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';  // Import the auth store
import { useCartStore } from '@/store/cart'; // Adjust the path as necessary
import axios from 'axios';

const cartStore = useCartStore();


const showDropdown = ref(false);
const authStore = useAuthStore();
const router = useRouter();

const api_base_url = import.meta.env.VITE_API_BASE_URL;



let dropdownTimeout;

const showDropdownWithDelay = (show) => {
  clearTimeout(dropdownTimeout);
  if (show) {
    // Small delay to keep the dropdown visible while moving the mouse
    dropdownTimeout = setTimeout(() => {
      showDropdown.value = true;
    }, 50); // Adjust delay as needed
  } else {
    dropdownTimeout = setTimeout(() => {
      showDropdown.value = false;
    }, 200); // Delay to close dropdown after mouse leaves
  }
};


// Fetch user data from API
const getUserData = async () => {
  try {
    const response = await axios.get(
      `${api_base_url}/api/accounts/users/${authStore.user.id}/`,
      { withCredentials: true }
    );
    user.value = {
      ...response.data,
      user_address: response.data.user_address || {
        full_name: '',
        street_address: '',
        street_address2: '',
        city: '',
        state: '',
        zip_code: '',
        country: ''
      }
    };
  } catch (error) {
  }
};

onMounted(() => {
  if (authStore.isAuthenticated) {
    getUserData();
  }
});

// Handle Logout functionality
const handleLogout = async () => {
  await authStore.logout();  // Wait for the logout method to finish
  router.push('/'); // Redirect to login page
};



</script>



<style scoped>
/* Optional additional styles can go here */
</style>
