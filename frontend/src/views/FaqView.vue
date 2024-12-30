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
        <!-- Loop through FAQ items -->
        <div v-for="(faq, index) in faqs" :key="faq.id" class="faq-item bg-white rounded-lg shadow-lg transform hover:scale-105 transition-all duration-300">
          <div class="flex justify-between items-center p-6 cursor-pointer hover:bg-[#ff9e00] rounded-lg group">
            <h3 class="text-2xl font-semibold text-[#1c1c1c] group-hover:text-white transition duration-300">{{ faq.question }}</h3>
            <i class="pi pi-chevron-down text-xl text-[#ff6f00] group-hover:text-white transition duration-300"></i>
          </div>
          <div class="p-6 bg-[#f7f7f7] rounded-b-lg">
            <p class="text-[#1c1c1c]">{{ faq.answer }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

export default {
  setup() {
    // Reactive state to store FAQ data
    const faqs = ref([]);
    const api_base_url = import.meta.env.VITE_API_BASE_URL;


    // Function to fetch FAQs from the backend
    const fetchFAQs = async () => {
      try {
        const response = await axios.get(`${api_base_url}/api/faqs/`); // Replace with your API endpoint
        faqs.value = response.data; // Store the fetched data in the faqs ref
      } catch (error) {
        console.error("Error fetching FAQs:", error);
      }
    };

    // Fetch FAQs when the component is mounted
    onMounted(fetchFAQs);

    // Return the reactive state so it can be used in the template
    return { faqs };
  }
};
</script>

<style scoped>
/* Add any additional styles here */
</style>
