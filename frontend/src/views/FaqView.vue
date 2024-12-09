<template>
    <section id="faq" class="faq py-20 bg-gradient-to-r from-[#ff6f00] to-[#ff9e00] text-white relative">
  <!-- Background Decorative Elements -->
  <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-50"></div>
  <div class="absolute bottom-1/4 left-1/4 w-24 h-24 bg-[#ff6f00] rounded-full opacity-20 animate-pulse"></div>
  <div class="absolute top-1/4 right-1/4 w-36 h-36 bg-[#ff6f00] rounded-full opacity-30 animate-pulse"></div>

  <div class="container mx-auto text-center relative z-10">
    <!-- Section Title -->
    <h2 class="text-4xl sm:text-5xl font-extrabold mb-12 text-yellow-500 animate__animated animate__fadeIn animate__delay-1s">
      Frequently Asked Questions
    </h2>

    <!-- FAQ Accordion -->
    <div class="space-y-6">
      <!-- Question 1 -->
      <div class="faq-item bg-white rounded-lg shadow-lg transform hover:scale-105 transition-all duration-300">
        <div class="flex justify-between items-center p-6 cursor-pointer hover:bg-[#ff9e00] rounded-lg group">
          <h3 class="text-2xl font-semibold text-[#1c1c1c] group-hover:text-white transition duration-300">What types of equipment do you offer?</h3>
          <i class="pi pi-chevron-down text-xl text-[#ff6f00] group-hover:text-white transition duration-300"></i>
        </div>
        <div class="p-6 bg-[#f7f7f7] rounded-b-lg">
          <p class="text-[#1c1c1c]">
            We offer a wide range of construction and industrial equipment, including excavators, bulldozers, cranes, generators, and more. Our inventory is constantly updated to meet your needs.
          </p>
        </div>
      </div>

      <!-- Question 2 -->
      <div class="faq-item bg-white rounded-lg shadow-lg transform hover:scale-105 transition-all duration-300">
        <div class="flex justify-between items-center p-6 cursor-pointer hover:bg-[#ff9e00] rounded-lg group">
          <h3 class="text-2xl font-semibold text-[#1c1c1c] group-hover:text-white transition duration-300">How do I book equipment?</h3>
          <i class="pi pi-chevron-down text-xl text-[#ff6f00] group-hover:text-white transition duration-300"></i>
        </div>
        <div class="p-6 bg-[#f7f7f7] rounded-b-lg">
          <p class="text-[#1c1c1c]">
            You can easily book equipment online by browsing our website, selecting the equipment you need, and filling out the booking form with your preferred rental dates. Once confirmed, we'll take care of the rest!
          </p>
        </div>
      </div>

      <!-- Question 3 -->
      <div class="faq-item bg-white rounded-lg shadow-lg transform hover:scale-105 transition-all duration-300">
        <div class="flex justify-between items-center p-6 cursor-pointer hover:bg-[#ff9e00] rounded-lg group">
          <h3 class="text-2xl font-semibold text-[#1c1c1c] group-hover:text-white transition duration-300">Do you offer delivery services?</h3>
          <i class="pi pi-chevron-down text-xl text-[#ff6f00] group-hover:text-white transition duration-300"></i>
        </div>
        <div class="p-6 bg-[#f7f7f7] rounded-b-lg">
          <p class="text-[#1c1c1c]">
            Yes, we offer fast and reliable delivery services for all equipment rentals. You can choose the delivery option at checkout, and we'll ensure your equipment arrives on time and in great condition.
          </p>
        </div>
      </div>

      <!-- Question 4 -->
      <div class="faq-item bg-white rounded-lg shadow-lg transform hover:scale-105 transition-all duration-300">
        <div class="flex justify-between items-center p-6 cursor-pointer hover:bg-[#ff9e00] rounded-lg group">
          <h3 class="text-2xl font-semibold text-[#1c1c1c] group-hover:text-white transition duration-300">Can I extend my rental period?</h3>
          <i class="pi pi-chevron-down text-xl text-[#ff6f00] group-hover:text-white transition duration-300"></i>
        </div>
        <div class="p-6 bg-[#f7f7f7] rounded-b-lg">
          <p class="text-[#1c1c1c]">
            Yes, we offer flexible rental extensions based on availability. You can extend your rental period by contacting us before your current rental expires.
          </p>
        </div>
      </div>

      <!-- Question 5 -->
      <div class="faq-item bg-white rounded-lg shadow-lg transform hover:scale-105 transition-all duration-300">
        <div class="flex justify-between items-center p-6 cursor-pointer hover:bg-[#ff9e00] rounded-lg group">
          <h3 class="text-2xl font-semibold text-[#1c1c1c] group-hover:text-white transition duration-300">What happens if the equipment gets damaged?</h3>
          <i class="pi pi-chevron-down text-xl text-[#ff6f00] group-hover:text-white transition duration-300"></i>
        </div>
        <div class="p-6 bg-[#f7f7f7] rounded-b-lg">
          <p class="text-[#1c1c1c]">
            We provide optional insurance plans that cover accidental damage. Without insurance, the renter is responsible for repair or replacement costs.
          </p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Optional: Add an animation library like Animate.css for smooth transitions -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>

</template>