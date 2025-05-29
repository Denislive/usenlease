<template>
  <div class="bg-[#1c1c1c] p-1 sticky top-0 z-50">
    <div class="w-12/12 md:w-6/6 lg:w-6/6 xl:w-6/6 mx-auto px-2">

      <header class="text-white flex justify-between items-center">
        <!-- Logo -->
        <RouterLink :to="{ name: 'home' }" class="flex items-center focus:outline-none rounded" aria-label="Home">
          <img src="../assets/images/dark_logo.png" alt="Company Logo" class="h-16 w-auto" loading="eager" width="64"
            height="64">
        </RouterLink>

        <!-- Role Switch (Authenticated Users) -->
        <div v-if="authStore.isAuthenticated"
          class="hidden md:flex items-center justify-between bg-[#121212] border border-gray-700 p-3 rounded-lg shadow"
          aria-label="Role switcher">
          <div class="flex items-center space-x-3">
            <span class="text-sm text-gray-300">
              Switch to {{ authStore.user?.role === 'lessor' ? 'lessee' : 'lessor' }}:
            </span>
            <label for="role-toggle" class="inline-flex relative items-center cursor-pointer">
              <input type="checkbox" id="role-toggle" v-model="authStore.isOn" class="sr-only peer"
                @change="authStore.updateUserRole()"
                :aria-label="`Switch to ${authStore.user?.role === 'lessor' ? 'lessee' : 'lessor'} role`" />
              <div
                class="w-11 h-6 bg-gray-700 border border-gray-500 rounded-full peer-checked:bg-[#ffc107] peer-checked:after:translate-x-5 after:content-[''] after:absolute after:left-0.5 after:top-0.5 after:w-5 after:h-5 after:rounded-full after:bg-gray-300 after:shadow-lg transition-all"
                aria-hidden="true"></div>
            </label>
          </div>
        </div>

        <!-- Authenticated User Menu -->
        <div v-if="authStore.isAuthenticated" class="flex items-center space-x-4">
          <!-- Browse Items Button for Lessee -->
          <RouterLink :to="{ name: 'categories' }"
            class="focus:outline-none focus:ring-2 focus:ring-[#ffc107] focus:ring-offset-2 focus:ring-offset-[#1c1c1c] rounded-lg">
            <button
              class="px-4 py-2 bg-gradient-to-r from-[#ff6f00] to-[#ffc107] text-white font-semibold rounded-lg shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-xl active:scale-95"
              aria-label="Browse items">
              Browse Items
            </button>
          </RouterLink>

          <!-- Lease Out Button for Lessor -->
          <RouterLink v-if="authStore.user.role === 'lessor'" :to="{ name: 'list-item' }"
            class="hidden md:block focus:outline-none focus:ring-2 focus:ring-[#ffc107] focus:ring-offset-2 focus:ring-offset-[#1c1c1c] rounded-lg">
            <button
              class="px-4 py-2 bg-[#ffc107] text-[#1c1c1c] font-semibold rounded-lg shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-xl active:scale-95"
              aria-label="Lease out item">
              Lease Out
            </button>
          </RouterLink>

          <!-- Equipment Icon for Lessor -->
          <div v-if="authStore.user.role === 'lessor'" class="relative">
            <RouterLink to="/profile?section=my-equipments" class="flex items-center relative focus:outline-none"
              aria-label="My equipment">
              <i class="pi pi-bars text-3xl mx-2" aria-hidden="true"></i>
              <span v-if="store.userEquipments.length > 0"
                class="absolute -top-1 -right-0 bg-red-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center"
                aria-hidden="true">
                {{ Math.min(store.userEquipments.length, 9) }}{{ store.userEquipments.length > 9 ? '+' : '' }}
              </span>
            </RouterLink>
          </div>

          <!-- Cart Icon for Lessee -->
          <div v-if="authStore.user.role === 'lessee'" class="relative">
            <RouterLink to="/cart" class="flex items-center relative focus:outline-none" aria-label="Shopping cart">
              <i class="pi pi-shopping-cart text-3xl mx-2" aria-hidden="true"></i>
              <span v-if="cartStore.cart.length > 0"
                class="absolute -top-1 -right-2 bg-red-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center"
                aria-hidden="true">
                {{ Math.min(cartStore.cart.length, 9) }}{{ cartStore.cart.length > 9 ? '+' : '' }}
              </span>
            </RouterLink>
          </div>

          <!-- Profile Dropdown -->
          <div class="relative hidden lg:block" @mouseenter="showDropdownWithDelay(true)"
            @mouseleave="showDropdownWithDelay(false)" @focusin="showDropdown = true" @focusout="showDropdown = false">
            <button
              class="flex items-center space-x-2 focus:outline-none focus:ring-2 focus:ring-[#ffc107] rounded-full"
              aria-label="User menu" aria-haspopup="true" :aria-expanded="showDropdown">
              <img :src="`${authStore.user?.image}`"
                :alt="authStore.user?.first_name ? authStore.user?.first_name.substring(0, 2).toUpperCase() : 'User'"
                class="w-10 h-10 rounded-full border-2 border-gray-300 object-cover user-avatar" width="40"
                height="40" />


            </button>
            <transition enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95">
              <div v-show="showDropdown"
                class="absolute right-0 mt-2 w-48 bg-[#1c1c1c] rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 py-1 z-10"
                role="menu" aria-orientation="vertical" aria-labelledby="user-menu">
                <RouterLink to="/new-profile"
                  class="block px-4 py-2 text-white hover:bg-gray-800 focus:bg-gray-800 focus:outline-none"
                  role="menuitem" @click="showDropdown = false">
                  Profile
                </RouterLink>
                <button @click="handleLogout"
                  class="w-full text-left px-4 py-2 text-white hover:bg-red-600 focus:bg-red-600 focus:outline-none"
                  role="menuitem">
                  Logout
                </button>
              </div>
            </transition>
          </div>
        </div>

        <!-- Not Authenticated User Menu -->
        <div v-else class="flex items-center space-x-4">
          <!-- Browse Items Button -->
          <RouterLink :to="{ name: 'categories' }"
            class="hidden lg:block focus:outline-none focus:ring-2 focus:ring-[#ffc107] focus:ring-offset-2 focus:ring-offset-[#1c1c1c] rounded-lg">
            <button
              class="px-6 py-2 bg-gradient-to-r from-[#ff6f00] to-[#ffc107] text-white font-semibold rounded-lg shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-xl active:scale-95"
              aria-label="Browse items">
              Browse Items
            </button>
          </RouterLink>

          <!-- Login Button -->
          <RouterLink to="/login"
            class="hidden md:block focus:outline-none focus:ring-2 focus:ring-[#ffc107] focus:ring-offset-2 focus:ring-offset-[#1c1c1c] rounded-lg">
            <button
              class="px-6 py-2 text-white font-semibold rounded-lg shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-xl active:scale-95"
              aria-label="Login">
              Login
            </button>
          </RouterLink>

          <!-- Lease Out Button -->
          <RouterLink :to="{ name: 'list-item' }"
            class="focus:outline-none focus:ring-2 focus:ring-[#ffc107] focus:ring-offset-2 focus:ring-offset-[#1c1c1c] rounded-lg">
            <button
              class="px-6 py-2 bg-[#ffc107] text-[#1c1c1c] font-semibold rounded-lg shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-xl active:scale-95"
              aria-label="Lease out equipment">
              Lease Out
            </button>
          </RouterLink>

          <!-- Cart Icon -->
          <div class="relative">
            <RouterLink to="/cart" class="flex items-center relative focus:outline-none" aria-label="Shopping cart">
              <i class="pi pi-shopping-cart text-3xl mx-2" aria-hidden="true"></i>
              <span v-if="cartStore.cart.length > 0"
                class="absolute -top-1 -right-2 bg-red-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center"
                aria-hidden="true">
                {{ Math.min(cartStore.cart.length, 9) }}{{ cartStore.cart.length > 9 ? '+' : '' }}
              </span>
            </RouterLink>
          </div>
        </div>
      </header>
    </div>
  </div>

  <!-- Mobile Bottom Navigation -->
  <nav class="fixed bottom-0 left-0 right-0 bg-[#1c1c1c] text-white p-2 shadow-lg md:hidden z-50"
    aria-label="Mobile navigation">
    <div class="flex justify-around items-center">
      <div class="text-center">
        <RouterLink to="/" class="flex flex-col items-center p-2 focus:outline-none focus:text-[#ffc107]"
          aria-label="Home">
          <i class="pi pi-home text-xl" aria-hidden="true"></i>
          <small class="text-xs">Home</small>
        </RouterLink>
      </div>

      <!-- Conditional Links for Authenticated Users -->
      <template v-if="authStore.isAuthenticated">
        <div v-if="authStore.user.role === 'lessor'" class="text-center">
          <RouterLink to="/list-item" class="flex flex-col items-center p-2 focus:outline-none focus:text-[#ffc107]"
            aria-label="List item">
            <i class="pi pi-plus text-xl" aria-hidden="true"></i>
            <small class="text-xs">List</small>
          </RouterLink>
        </div>
        <div v-if="authStore.user.role === 'lessee'" class="text-center">
          <RouterLink to="/categories" class="flex flex-col items-center p-2 focus:outline-none focus:text-[#ffc107]"
            aria-label="Browse categories">
            <i class="pi pi-search text-xl" aria-hidden="true"></i>
            <small class="text-xs">Browse</small>
          </RouterLink>
        </div>
      </template>

      <!-- Links for Unauthenticated Users -->
      <template v-else>
        <div class="text-center">
          <RouterLink to="/profile?section=reports"
            class="flex flex-col items-center p-2 focus:outline-none focus:text-[#ffc107]" aria-label="Reports">
            <i class="pi pi-bookmark text-xl" aria-hidden="true"></i>
            <small class="text-xs">Reports</small>
          </RouterLink>
        </div>
      </template>

      <!-- Messages Link -->
      <div class="text-center">
        <RouterLink to="/profile?section=chats"
          class="flex flex-col items-center p-2 focus:outline-none focus:text-[#ffc107]" aria-label="Messages">
          <i class="pi pi-comments text-xl" aria-hidden="true"></i>
          <small class="text-xs">Messages</small>
        </RouterLink>
      </div>

      <!-- Profile Link -->
      <div class="text-center">
        <RouterLink to="/new-profile" class="flex flex-col items-center p-2 focus:outline-none focus:text-[#ffc107]"
          aria-label="Profile">
          <i class="pi pi-user text-xl" aria-hidden="true"></i>
          <small class="text-xs">Profile</small>
        </RouterLink>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import { useCartStore } from '@/store/cart';
import { useEquipmentsStore } from '@/store/equipments';
import { useCompanyInfoStore } from '@/store/company';
import useNotifications from '@/store/notification';

// Constants
const MAX_BADGE_COUNT = 9;

// Stores
const authStore = useAuthStore();
const cartStore = useCartStore();
const store = useEquipmentsStore();
const company = useCompanyInfoStore();
const { showNotification } = useNotifications();
const router = useRouter();

// State
const showDropdown = ref(false);
let dropdownTimeout = null;

// Methods
const showDropdownWithDelay = (show) => {
  clearTimeout(dropdownTimeout);
  dropdownTimeout = setTimeout(() => {
    showDropdown.value = show;
  }, show ? 50 : 200);
};


const handleLogout = async () => {
  try {
    await authStore.logout();
  } catch (error) {
    console.error('Logout failed:', error);
    showNotification({
      title: 'Logout Error',
      message: 'There was an error logging out. Please try again.',
      type: 'error'
    });
  }
};

// Lifecycle Hooks
onMounted(async () => {
  if (authStore.isAuthenticated) {
    try {
      await Promise.all([
        authStore.getUserData(),
        store.fetchUserEquipments()
      ]);
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  }

  try {
    await company.fetchCompanyInfo();
  } catch (error) {
    console.error('Failed to load company info:', error);
  }
});
</script>

<style scoped>
.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  background: #ddd;
  /* Light gray background */
  color: #1c1c1c;
}

/* Smooth transitions for interactive elements */
.router-link-active {
  @apply text-[#ffc107];
}

/* Badge animation */
span[aria-hidden="true"] {
  @apply transition-transform duration-200;
}

/* Mobile nav link active state */
.router-link-active i,
.router-link-active small {
  @apply text-[#ffc107];
}
</style>