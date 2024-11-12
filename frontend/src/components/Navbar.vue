<script setup>
import { ref, watchEffect } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';  // Import the auth store
import { useCartStore } from '@/store/cart'; // Adjust the path as necessary
const cartStore = useCartStore();



const authStore = useAuthStore();
const router = useRouter();

// Handle Logout functionality
const handleLogout = async () => {
  await authStore.logout();  // Wait for the logout method to finish
  router.push('/'); // Redirect to login page
};

// Watch authentication state to handle navigation or component updates if necessary
watchEffect(() => {
  if (!authStore.isAuthenticated) {

    console.log("User is not authenticated");
  }
});


</script>


<template>
  <div class="bg-[#1c1c1c] p-4 sticky top-0 z-50">
    <div class="w-11/12 md:w-5/6 lg:w-5/6 mx-auto">
      <header class="text-white flex justify-between items-center">
        <RouterLink :to="{ name: 'home' }" class="flex items-center">
          <img src="@/assets/images/logo.jpeg" alt="Use N lease Logo" class="h-20" />
        </RouterLink>

        <div class="flex items-center space-x-4">
          <RouterLink :to="{name: 'categories'}" class="hidden md:block text-xl">
            CATEGORIES
          </RouterLink>

          <!-- Conditionally show Login or Logout based on isAuthenticated -->
          <RouterLink v-if="!authStore.isAuthenticated" to="/login" class="hidden md:block hover:underline text-xl">
            Login
          </RouterLink>
          <button v-else @click="handleLogout" class="hidden md:block hover:underline text-xl">
            Logout
          </button>

          <RouterLink :to="{ name: 'list-item' }"
            class="bg-[#ffc107] text-black py-2 px-4 rounded hover:bg-yellow-400 transition flex items-center"
            aria-label="Add a new item">
            Lease
          </RouterLink>

          <div class="relative">
            <RouterLink to="/cart" class="flex items-center">
              <i class="pi pi-shopping-cart text-2xl"></i>
              <span v-if="!authStore.isAuthenticated" class="absolute top-[-15px] right-[-20px] bg-red-600 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">{{ cartStore.totalCartItems  }}</span>
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
      <div class="text-center">
        <RouterLink to="/saved" class="flex flex-col items-center">
          <i class="pi pi-bookmark text-xl"></i>
          <small>Saved</small>
        </RouterLink>
      </div>
      <div class="text-center">
        <a href="#" class="flex flex-col items-center" data-open="listEquipmentModal">
          <i class="pi pi-plus text-xl"></i>
          <small>List</small>
        </a>
      </div>
      <div class="text-center">
        <RouterLink to="/messages" class="flex flex-col items-center">
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


<style scoped>

/* Optional additional styles can go here */
</style>
