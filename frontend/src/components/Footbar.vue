<template>
  <footer class="bg-[#1c1c1c] text-white py-16 relative z-20">
    <!-- Background Decorative Effect -->
    <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#ff6f00] to-[#1c1c1c] opacity-20"></div>

    <div class="container mx-auto px-4 relative z-10">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center md:text-left">
        <!-- Company Information -->
        <div class="animate__animated animate__fadeIn animate__delay-1s">
          <h2 class="text-3xl font-extrabold text-[#ffc107] mb-4">UseNLease Co.</h2>
          <p class="text-lg mb-4">Your one-stop solution for all your equipment rental needs. Renting made easy, anywhere, anytime!</p>
          <p>
            <a href="mailto:info@usenlease.com" class="text-[#ffc107] hover:underline">info@usenlease.com</a>
          </p>
        </div>

        <!-- Quick Links -->
        <div class="animate__animated animate__fadeIn animate__delay-2s">
          <h3 class="text-xl font-semibold mb-4">Quick Links</h3>
          <ul class="space-y-4">
            <li><RouterLink to="/" class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">Home</RouterLink></li>
            <li><RouterLink to="/about" class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">About Us</RouterLink></li>
            <li><RouterLink to="/services" class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">Services</RouterLink></li>
            <li><RouterLink to="/contact" class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">Contact</RouterLink></li>
            <li><RouterLink to="/faq" class="hover:text-[#ffc107] transition duration-300 ease-in-out transform hover:scale-105">FAQ</RouterLink></li>
          </ul>
        </div>

        <!-- Social Media Links -->
        <div class="animate__animated animate__fadeIn animate__delay-3s">
          <h3 class="text-xl font-semibold mb-4">Follow Us</h3>
          <div class="flex justify-center space-x-6">
            <a href="#" class="text-[#ffc107] hover:text-[#ff6f00] transition duration-300 ease-in-out transform hover:scale-110">
              <i class="pi pi-facebook text-3xl"></i>
            </a>
            <a href="#" class="text-[#ffc107] hover:text-[#ff6f00] transition duration-300 ease-in-out transform hover:scale-110">
              <i class="pi pi-twitter text-3xl"></i>
            </a>
            <a href="#" class="text-[#ffc107] hover:text-[#ff6f00] transition duration-300 ease-in-out transform hover:scale-110">
              <i class="pi pi-instagram text-3xl"></i>
            </a>
            <a href="#" class="text-[#ffc107] hover:text-[#ff6f00] transition duration-300 ease-in-out transform hover:scale-110">
              <i class="pi pi-linkedin text-3xl"></i>
            </a>
          </div>
        </div>
      </div>

      <!-- Footer Bottom Section -->
      <div class="border-t border-gray-700 mt-8 pt-4 text-center text-sm text-[#ccc]">
        <p>&copy; 2024 UseNLease Co. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
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
    0% { opacity: 0; }
    100% { opacity: 1; }
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
