<template>
  <footer class="bg-[#1c1c1c] text-white py-16 relative z-20">
    <!-- Background Decorative Effect -->
    <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#ff6f00] to-[#1c1c1c] opacity-20"></div>

    <div class="container mx-auto px-4 relative z-10">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center md:text-left">
        <!-- Company Information -->
        <div class="animate__animated animate__fadeIn animate__delay-1s">
          <h2 class="text-3xl font-extrabold text-[#ffc107] mb-4">{{ companyInfoStore.companyInfo?.name }}</h2>
          <p class="text-lg mb-4">{{ companyInfoStore.companyInfo?.about }}</p>
          <p>
            <a href="mailto:info@usenlease.com" class="text-[#ffc107] hover:underline">{{
              companyInfoStore.companyInfo?.email }}</a>
          </p>
        </div>

        <!-- Quick Links -->
        <div class="animate__animated animate__fadeIn animate__delay-2s">
          <h3 class="text-xl font-semibold mb-4">Quick Links</h3>
          <ul class="space-y-4">
            <li>
              <RouterLink to="/"
                class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">Home
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/about"
                class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">About Us
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/services"
                class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">Services
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/contact"
                class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">Contact
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/faq"
                class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">FAQ
              </RouterLink>
            </li>

            <li>
              <RouterLink to="/terms-conditions"
                class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">Terms and Conditions
              </RouterLink>
            </li>

            <li>
              <RouterLink to="/privacy-cookie-notice"
                class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">Privacy and Cookie Notice
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Social Media Links -->
        <div class="animate__animated animate__fadeIn animate__delay-3s">
          <h3 class="text-xl font-semibold mb-4">Follow Us</h3>
          <div class="flex justify-center space-x-6">
            <!-- Facebook -->
            <a v-if="companyInfoStore.companyInfo?.facebook_link" :href="companyInfoStore.companyInfo.facebook_link"
              class="text-[#ffc107] hover:text-[#ff6f00] transition duration-300 ease-in-out transform hover:scale-110"
              target="_blank" rel="noopener noreferrer">
              <i class="pi pi-facebook text-3xl"></i>
            </a>

            <!-- Twitter -->
            <a v-if="companyInfoStore.companyInfo?.twitter_link" :href="companyInfoStore.companyInfo.twitter_link"
              class="text-[#ffc107] hover:text-[#ff6f00] transition duration-300 ease-in-out transform hover:scale-110"
              target="_blank" rel="noopener noreferrer">
              <i class="pi pi-twitter text-3xl"></i>
            </a>

            <!-- Instagram -->
            <a v-if="companyInfoStore.companyInfo?.instagram_link" :href="companyInfoStore.companyInfo.instagram_link"
              class="text-[#ffc107] hover:text-[#ff6f00] transition duration-300 ease-in-out transform hover:scale-110"
              target="_blank" rel="noopener noreferrer">
              <i class="pi pi-instagram text-3xl"></i>
            </a>

            <!-- LinkedIn -->
            <a v-if="companyInfoStore.companyInfo?.linkedin_link" :href="companyInfoStore.companyInfo.linkedin_link"
              class="text-[#ffc107] hover:text-[#ff6f00] transition duration-300 ease-in-out transform hover:scale-110"
              target="_blank" rel="noopener noreferrer">
              <i class="pi pi-linkedin text-3xl"></i>
            </a>
          </div>
        </div>

      </div>

      <!-- Footer Bottom Section -->
      <div class="border-t border-gray-700 mt-8 pt-4 text-center text-sm text-[#ccc]">
        <p>&copy; 2024 {{ companyInfoStore.companyInfo?.name }}. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { useCompanyInfoStore } from '@/store/company';
const companyInfoStore = useCompanyInfoStore();


const api_base_url = import.meta.env.VITE_API_BASE_URL;


// Script content can be added here if needed
</script>

<style scoped>
/* Hover effects */
.hover\:scale-105:hover {
  transform: scale(1.05);
}

.hover\:scale-110:hover {
  transform: scale(1.1);
}

/* Fade-in animation */
@keyframes fadeIn {
  0% {
    opacity: 0;
  }

  100% {
    opacity: 1;
  }
}

.animate__fadeIn {
  animation: fadeIn 1s ease-in-out;
}

/* Adjust padding for responsive design */
@media (max-width: 768px) {
  .container {
    padding-left: 2rem;
    padding-right: 2rem;
  }
}
</style>
