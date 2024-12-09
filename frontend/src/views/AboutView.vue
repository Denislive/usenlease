<template>
<section class="about bg-gradient-to-r from-[#1c1c1c] to-[#ff6f00] py-16 text-white relative overflow-hidden">
  <!-- Background Decorative Elements -->
  <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-40"></div>
  <div class="absolute top-1/4 right-1/4 w-24 h-24 bg-[#ff6f00] rounded-full opacity-30 animate-pulse"></div>
  <div class="absolute bottom-1/4 left-1/4 w-36 h-36 bg-[#ff9e00] rounded-full opacity-20 animate-pulse"></div>

  <div class="container mx-auto text-center relative z-10">
    <!-- About Title -->
    <h2 class="text-4xl sm:text-5xl font-semibold mb-6 text-yellow-500 animate__animated animate__fadeIn animate__delay-1s">
      About Us
    </h2>

    <!-- Mission Statement -->
    <p class="text-lg sm:text-xl mb-12 max-w-3xl mx-auto leading-relaxed animate__animated animate__fadeIn animate__delay-2s">
      At <span class="font-bold text-[#ffc107]">UseNLease</span>, we are dedicated to providing high-quality equipment for all your needs. Whether you're working on a construction project, landscaping, or just need the right tool for a weekend project, we have a wide range of reliable and well-maintained equipment at your fingertips. Our mission is to make equipment rental easy, affordable, and accessible for everyone.
    </p>

    <!-- Values Section with Icons -->
    <div class="flex flex-col md:flex-row justify-center items-center space-y-8 md:space-y-0 md:space-x-8">
      <!-- Value 1: Quality -->
      <div class="w-60 bg-[#ff6f00] text-white p-6 rounded-xl shadow-lg transform hover:scale-105 transition duration-300 ease-in-out">
        <div class="mb-4 flex justify-center items-center">
          <i class="pi pi-cog text-4xl"></i>
        </div>
        <h3 class="text-2xl font-bold mb-4">Quality</h3>
        <p class="text-lg">
          We ensure all our equipment is of the highest quality, regularly maintained, and ready for use.
        </p>
      </div>

      <!-- Value 2: Customer Support -->
      <div class="w-60 bg-[#ff9e00] text-white p-6 rounded-xl shadow-lg transform hover:scale-105 transition duration-300 ease-in-out">
        <div class="mb-4 flex justify-center items-center">
          <i class="pi pi-headset text-4xl"></i>
        </div>
        <h3 class="text-2xl font-bold mb-4">Customer Support</h3>
        <p class="text-lg">
          Our team is always available to assist you in choosing the right equipment and ensuring smooth delivery and returns.
        </p>
      </div>

      <!-- Value 3: Convenience -->
      <div class="w-60 bg-[#ff6f00] text-white p-6 rounded-xl shadow-lg transform hover:scale-105 transition duration-300 ease-in-out">
        <div class="mb-4 flex justify-center items-center">
          <i class="pi pi-thumbs-up text-4xl"></i>
        </div>
        <h3 class="text-2xl font-bold mb-4">Convenience</h3>
        <p class="text-lg">
          Rent your equipment effortlessly online and get it delivered to your location quickly.
        </p>
      </div>
    </div>

    <!-- Call to Action -->
    <div class="mt-12">
      <a href="#contact" class="bg-[#ffc107] text-[#1c1c1c] py-3 px-8 rounded-full text-lg font-semibold hover:bg-[#ff9e00] transition duration-300 transform hover:scale-110">
        Contact Us Today
      </a>
    </div>
  </div>
</section>

</template>

<style>

</style>
