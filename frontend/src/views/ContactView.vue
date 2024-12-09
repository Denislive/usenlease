<template>
    <section id="contact" class="contact bg-gradient-to-r from-[#1c1c1c] to-[#ff6f00] py-16 text-white relative overflow-hidden">
  <!-- Background Decorative Elements -->
  <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-40"></div>
  <div class="absolute bottom-1/4 right-1/4 w-24 h-24 bg-[#ff9e00] rounded-full opacity-30 animate-pulse"></div>

  <div class="container mx-auto text-center relative z-10">
    <!-- Contact Title -->
    <h2 class="text-4xl sm:text-5xl font-semibold mb-6 text-yellow-500 animate__animated animate__fadeIn animate__delay-1s">
      Get In Touch
    </h2>

    <!-- Contact Info -->
    <div class="mb-12 animate__animated animate__fadeIn animate__delay-2s">
      <p class="text-lg sm:text-xl mb-4">
        We're here to help you with all your equipment rental needs! Reach out to us, and our team will respond as soon as possible.
      </p>
      <div class="flex justify-center items-center space-x-12">
        <!-- Email Icon -->
        <div class="flex items-center space-x-3">
          <i class="pi pi-envelope text-3xl text-[#ffc107]"></i>
          <a href="mailto:support@example.com" class="text-lg hover:text-[#ff6f00] transition duration-300">support@example.com</a>
        </div>

        <!-- Phone Icon -->
        <div class="flex items-center space-x-3">
          <i class="pi pi-phone text-3xl text-[#ffc107]"></i>
          <a href="tel:+1234567890" class="text-lg hover:text-[#ff6f00] transition duration-300">+1 (234) 567-890</a>
        </div>

        <!-- Location Icon -->
        <div class="flex items-center space-x-3">
          <i class="pi pi-map-marker text-3xl text-[#ffc107]"></i>
          <p class="text-lg">123 Equipment St, City, Country</p>
        </div>
      </div>
    </div>

    <!-- Contact Form -->
    <div class="w-full sm:w-3/4 lg:w-1/2 mx-auto bg-white p-8 rounded-xl shadow-lg">
      <form>
        <!-- Name Field -->
        <div class="mb-6">
          <label for="name" class="block text-lg text-[#1c1c1c]">Your Name</label>
          <input type="text" id="name" class="w-full p-3 mt-2 border border-[#ddd] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff6f00]" placeholder="Enter your name" required>
        </div>

        <!-- Email Field -->
        <div class="mb-6">
          <label for="email" class="block text-lg text-[#1c1c1c]">Your Email</label>
          <input type="email" id="email" class="w-full p-3 mt-2 border border-[#ddd] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff6f00]" placeholder="Enter your email" required>
        </div>

        <!-- Message Field -->
        <div class="mb-6">
          <label for="message" class="block text-lg text-[#1c1c1c]">Your Message</label>
          <textarea id="message" class="w-full p-3 mt-2 border border-[#ddd] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff6f00]" rows="5" placeholder="Write your message here" required></textarea>
        </div>

        <!-- Submit Button -->
        <button type="submit" class="bg-[#ff6f00] text-white py-3 px-8 rounded-full text-lg font-semibold hover:bg-[#ff9e00] transition duration-300 transform hover:scale-110 w-full">
          Send Message
        </button>
      </form>
    </div>
  </div>
</section>

</template>