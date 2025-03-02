<script setup>
import Hero from '@/components/Hero.vue'
import Sidebar from '@/components/Sidebar.vue'
import Slider from '@/components/Slider.vue'
import Equipment from '@/components/Equipment.vue'
import MobileCategories from '@/components/MobileCategories.vue'
import { ref } from 'vue'
import Cookies from 'js-cookie'

const showBanner = ref(!Cookies.get('cookie_consent')) // Show banner if no consent cookie

// Handle accepting cookies
const acceptCookies = () => {
  Cookies.set('cookie_consent', 'accepted', { expires: 365 })
  showBanner.value = false
}
</script>

<template>
  <Hero />

  <div class="w-full mx-4 hidden md:block">
    <div class="grid grid-cols-12 gap-4 p-1">
      <!-- Sidebar Section -->
      <aside class="col-span-2 bg-gray-100 rounded p-2 max-h-[100vh] overflow-y-auto">
        <Sidebar />
      </aside>

      <!-- Main Content Section -->
      <main class="col-span-10 bg-gray-100 p-1 max-h-[100vh] overflow-y-auto">
        <Slider />
        <Equipment />
      </main>
    </div>
  </div>

  <div class="container p-2 md:hidden">
    <Equipment />
  </div>
  
  <!-- Privacy Banner -->
  <div v-if="showBanner" class="fixed bottom-0 left-0 w-full bg-gray-800 text-white p-4 z-50">
    <div class="max-w-4xl mx-auto flex flex-col md:flex-row justify-between items-center">
      <div>
        <h3 class="text-lg font-semibold">We Value Your Privacy</h3>
        <p class="text-sm mt-2">
          This website uses cookies to enhance your experience. By continuing to use this site, you agree to our use of cookies.
          <a
            href="/privacy-cookie-notice"
            class="underline text-blue-400 hover:text-blue-500"
          >
            Learn more.
          </a>
        </p>
      </div>
      <div class="mt-4 md:mt-0 flex space-x-4">
        <button
          @click="acceptCookies"
          class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md"
        >
          Accept
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
a {
  transition: color 0.3s ease;
}
</style>
