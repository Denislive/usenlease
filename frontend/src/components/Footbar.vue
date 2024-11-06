<template>
    <footer class="bg-[#1c1c1c] text-white py-8">
      <div class="container mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Company Information -->
          <div>
            <h2 class="text-xl font-bold mb-4">Equipment Rental Co.</h2>
            <p class="mb-2">Your one-stop solution for all your equipment rental needs.</p>
            <p>Contact us: <a href="mailto:info@equipmentrental.com" class="text-[#ffc107] hover:underline">info@equipmentrental.com</a></p>
          </div>
  
          <!-- Quick Links -->
          <div>
            <h3 class="text-lg font-semibold mb-4">Quick Links</h3>
            <ul class="space-y-2">
              <li><RouterLink to="/" class="hover:text-[#ffc107]">Home</RouterLink></li>
              <li><RouterLink to="/about" class="hover:text-[#ffc107]">About Us</RouterLink></li>
              <li><RouterLink to="/services" class="hover:text-[#ffc107]">Services</RouterLink></li>
              <li><RouterLink to="/contact" class="hover:text-[#ffc107]">Contact</RouterLink></li>
              <li><RouterLink to="/faq" class="hover:text-[#ffc107]">FAQ</RouterLink></li>
            </ul>
          </div>
  
          <!-- Social Media Links -->
          <div>
            <h3 class="text-lg font-semibold mb-4">Follow Us</h3>
            <div class="flex space-x-4">
              <a href="#" class="hover:text-[#ffc107]"><i class="pi pi-facebook text-2xl"></i></a>
              <a href="#" class="hover:text-[#ffc107]"><i class="pi pi-twitter text-2xl"></i></a>
              <a href="#" class="hover:text-[#ffc107]"><i class="pi pi-instagram text-2xl"></i></a>
              <a href="#" class="hover:text-[#ffc107]"><i class="pi pi-linkedin text-2xl"></i></a>
            </div>
          </div>
        </div>
  
        <div class="border-t border-gray-700 mt-8 pt-4 text-center">
          <p class="text-sm">&copy; 2024 Equipment Rental Co. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </template>
  
  <script setup>
  // Script content can be added here if needed
  </script>
  
  <style scoped>
  /* Additional styles can go here if needed */
  </style>