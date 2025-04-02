<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex flex-col items-center justify-center p-6">
    <div class="bg-white rounded-2xl shadow-xl p-8 md:p-10 text-center max-w-md w-full transform transition-all duration-300 hover:shadow-2xl">
      <div class="mb-6 animate-bounce">
        <i class="pi pi-map text-6xl text-[#ffc107]"></i>
      </div>
      
      <h1 class="text-4xl font-bold text-gray-800 mb-3">
        <span class="text-[#1c1c1c]">404</span> - Page Not Found
      </h1>
      
      <p class="text-gray-600 mb-6">
        Oops! The page you're looking for has wandered off. Let's get you back on track.
      </p>
      
      <div class="space-y-4">
        <RouterLink
          to="/"
          class="block w-full bg-[#1c1c1c] text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-800 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#ffc107] focus:ring-offset-2"
          aria-label="Return to home page"
        >
          <i class="pi pi-home mr-2"></i> Go to Homepage
        </RouterLink>
        
        <button
          @click="goBack"
          class="block w-full bg-white text-[#1c1c1c] py-3 px-6 rounded-lg font-medium border border-gray-300 hover:bg-gray-50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#ffc107] focus:ring-offset-2"
          aria-label="Go back to previous page"
        >
          <i class="pi pi-arrow-left mr-2"></i> Go Back
        </button>
      </div>
      
      <div class="mt-8 pt-6 border-t border-gray-200">
        <p class="text-sm text-gray-500 mb-2">Still lost? Try these helpful links:</p>
        <div class="flex justify-center space-x-4">
          <RouterLink 
            to="/categories" 
            class="text-sm text-[#1c1c1c] hover:text-[#ffc107] transition-colors"
            aria-label="Browse categories"
          >
            Browse
          </RouterLink>
          <RouterLink
           to="/terms-conditions" 
           class="text-sm text-[#1c1c1c] hover:text-[#ffc107] transition-colors"
           >
           Terms
          </RouterLink>
          <RouterLink
           to="/privacy-cookie-notice" 
           class="text-sm text-[#1c1c1c] hover:text-[#ffc107] transition-colors"
           >
           Privacy Policy
          </RouterLink>

          <RouterLink 
            to="/contact" 
            class="text-sm text-[#1c1c1c] hover:text-[#ffc107] transition-colors"
            aria-label="Contact support"
          >
            Contact Us
          </RouterLink>
        </div>
      </div>
    </div>
    
    <div class="mt-8 text-center">
      <p class="text-xs text-gray-400">
        Error code: 404 | {{ new Date().toLocaleDateString() }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1);
  } else {
    router.push('/');
  }
};
</script>

<style scoped>
.animate-bounce {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

/* Smooth transitions for interactive elements */
a, button {
  transition: all 0.2s ease;
}

</style>