<template>
  <section
    id="contact"
    class="contact bg-gradient-to-r from-[#1c1c1c] to-[#ff6f00] py-8 md:py-16 text-white relative overflow-hidden"
  >
    <!-- Background Decorative Elements -->
    <div
      class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-40"
    ></div>
    <div
      class="absolute bottom-1/4 right-1/4 w-16 h-16 md:w-24 md:h-24 bg-[#ff9e00] rounded-full opacity-30 animate-pulse hidden md:block"
    ></div>

    <div class="container mx-auto px-4 text-center relative z-10">
      <!-- Contact Title -->
      <h2
        class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-semibold mb-6 text-yellow-500 animate__animated animate__fadeIn animate__delay-1s"
      >
        Get In Touch
      </h2>

      <!-- Contact Info -->
      <div class="mb-8 md:mb-12 animate__animated animate__fadeIn animate__delay-2s">
        <p class="text-base sm:text-lg md:text-xl mb-4">
          We're here to help you with all your item rental needs! Reach out to us, and our team will respond as soon as possible.
        </p>
        <div
          class="flex flex-col md:flex-row justify-center items-center space-y-6 md:space-y-0 md:space-x-8"
        >
          <!-- Email Icon -->
          <div class="flex items-center space-x-3">
            <i class="pi pi-envelope text-2xl md:text-3xl text-[#ffc107]"></i>
            <a
              href="mailto:support@example.com"
              class="text-base md:text-lg hover:text-[#ff6f00] transition duration-300"
              >support@usenlease.com</a
            >
          </div>

          <!-- Phone Icon -->
          <div class="flex items-center space-x-3">
            <i class="pi pi-phone text-2xl md:text-3xl text-[#ffc107]"></i>
            <a
              href="tel:+1234567890"
              class="text-base md:text-lg hover:text-[#ff6f00] transition duration-300"
              >800 use n lease</a
            >
          </div>

          <!-- Location Icon -->
          <div class="flex items-center space-x-3">
            <i class="pi pi-map-marker text-2xl md:text-3xl text-[#ffc107]"></i>
            <p class="text-base md:text-lg">94577 Northern California, California, United States</p>
          </div>
        </div>
      </div>

      <!-- Contact Form -->
      <div
        class="w-full sm:w-11/12 md:w-3/4 lg:w-1/2 mx-auto bg-white p-6 sm:p-8 rounded-xl shadow-lg"
      >
        <form @submit="handleSubmit">
          <!-- Name Field -->
          <div class="mb-6">
            <label for="name" class="block text-base md:text-lg text-[#1c1c1c]"
              >Your Name</label
            >
            <input
              type="text"
              id="name"
              v-model="name"
              class="w-full p-3 mt-2 border border-[#ddd] text-[#1c1c1c] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff6f00]"
              placeholder="Enter your name"
              required
            />
          </div>

          <!-- Email Field -->
          <div class="mb-6">
            <label for="email" class="block text-base md:text-lg text-[#1c1c1c]"
              >Your Email</label
            >
            <input
              type="email"
              id="email"
              v-model="email"
              class="w-full p-3 mt-2 border border-[#ddd] text-[#1c1c1c] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff6f00]"
              placeholder="Enter your email"
              required
            />
          </div>

          <!-- Message Field -->
          <div class="mb-6">
            <label for="message" class="block text-base md:text-lg text-[#1c1c1c]"
              >Your Message</label
            >
            <textarea
              id="message"
              v-model="message"
              class="w-full p-3 mt-2 border border-[#ddd] text-[#1c1c1c] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff6f00]"
              rows="5"
              placeholder="Write your message here"
              required
            ></textarea>
          </div>

          <!-- Loading Indicator -->
          <div
            v-if="loading"
            class="mb-4 text-center text-[#ff6f00] font-semibold"
          >
            Sending your message...
          </div>

          <!-- Success Message -->
          <div
            v-if="successMessage"
            class="mb-4 text-center text-green-500 font-semibold"
          >
            {{ successMessage }}
          </div>

          <!-- Error Message -->
          <div
            v-if="errorMessage"
            class="mb-4 text-center text-red-500 font-semibold"
          >
            {{ errorMessage }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="bg-[#ff6f00] text-white py-3 px-8 rounded-full text-base md:text-lg font-semibold hover:bg-[#ff9e00] transition duration-300 transform hover:scale-105 w-full disabled:opacity-50"
          >
            Send Message
          </button>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import useNotifications from '@/store/notification.js'; // Import the notification service
const { showNotification } = useNotifications(); // Initialize notification service

// Reactive form fields
const name = ref('');
const email = ref('');
const message = ref('');
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const api_base_url = import.meta.env.VITE_API_BASE_URL;
// Submit handler
const handleSubmit = async (event) => {
  event.preventDefault(); // Prevent form default submission

  // Validate form fields
  if (!name.value || !email.value || !message.value) {
    errorMessage.value = 'All fields are required.';
    return;
  }

  try {
    loading.value = true;

    // Payload to send to the backend
    const payload = {
      name: name.value,
      email: email.value,
      message: message.value,
    };

    // Replace with your backend API endpoint
    const response = await axios.post(`${api_base_url}/api/contact/`, payload);

    // Handle successful submission
    if (response.status === 200 || response.status === 201) {
      showNotification(
        'Success',
        'Message sent successfully! We will get back to you shortly.',
        'success'
      );

      // Reset the form fields
      name.value = '';
      email.value = '';
      message.value = '';
    }
  } catch (error) {
    showNotification(
      'Error',
      'An error occurred while sending the message. Please try again later.',
      'error'
    );
  } finally {
    loading.value = false;
  }
};
</script>