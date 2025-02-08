<template>
  <footer class="bg-[#1c1c1c] text-gray-200 py-16 relative z-20 overflow-hidden">
    <!-- Background Decorative Effect -->
    <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#ff6f00] to-[#1c1c1c] opacity-20"></div>
    
    <!-- Floating Glow Effect -->
    <div class="absolute -top-10 left-1/3 w-32 h-32 bg-[#ff6f00] rounded-full blur-3xl opacity-10"></div>
    <div class="absolute bottom-0 right-1/4 w-24 h-24 bg-[#ffc107] rounded-full blur-2xl opacity-15"></div>

    <div class="container mx-auto px-8 md:px-16 relative z-10">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
        <!-- My Account -->
        <div class="group">
          <h3 class="text-xl font-semibold text-[#ffc107] mb-4 transition-all duration-300 group-hover:scale-105">My Account</h3>
          <ul class="space-y-3 pl-3">
            <li><RouterLink to="/cart" class="bullet-link">Cart</RouterLink></li>
            <li><RouterLink to="/messages" class="bullet-link">Messages</RouterLink></li>
            <li><RouterLink to="/orders" class="bullet-link">My Orders</RouterLink></li>
            <li><RouterLink to="/my-items" class="bullet-link">My Items</RouterLink></li>
          </ul>
        </div>

        <!-- Information -->
        <div class="group">
          <h3 class="text-xl font-semibold text-[#ffc107] mb-4 transition-all duration-300 group-hover:scale-105">Information</h3>
          <ul class="space-y-3 pl-3">
            <li><RouterLink to="/terms-conditions" class="bullet-link">Terms and Conditions</RouterLink></li>
            <li><RouterLink to="/privacy-policy" class="bullet-link">Privacy Policy</RouterLink></li>
            <li><RouterLink to="/contact" class="bullet-link">Contact Us</RouterLink></li>
          </ul>
        </div>

        <!-- Useful Links -->
        <div class="group">
          <h3 class="text-xl font-semibold text-[#ffc107] mb-4 transition-all duration-300 group-hover:scale-105">Useful Links</h3>
          <ul class="space-y-3 pl-3">
            <li><RouterLink to="/about" class="bullet-link">About Us</RouterLink></li>
            <li><RouterLink to="/faqs" class="bullet-link">FAQs</RouterLink></li>
          </ul>
        </div>

        <!-- Contact Us -->
        <div>
          <h3 class="text-xl font-semibold text-[#ffc107] mb-4">Contact Us</h3>
          <ul class="space-y-3 pl-3">
            <li class="flex items-start space-x-3">
              <i class="pi pi-map-marker text-xl text-gray-200"></i>
              <span class="leading-5">{{ formattedAddress }}</span>
            </li>
            <li class="flex items-center space-x-3">
              <i class="pi pi-clock text-xl text-gray-200"></i>
              <span>{{ companyInfoStore.companyInfo?.opening_hours }}</span>
            </li>
            <li class="flex items-center space-x-3">
              <i class="pi pi-envelope text-xl text-gray-200"></i>
              <a :href="'mailto:' + companyInfoStore.companyInfo?.email" class="hover:text-[#ffc107]">
                {{ companyInfoStore.companyInfo?.email }}
              </a>
            </li>
            <li class="flex items-center space-x-3">
              <i class="pi pi-phone text-xl text-gray-200"></i>
              <span>{{ companyInfoStore.companyInfo?.phone_number }}</span>
            </li>
            <li class="flex justify-start space-x-4 mt-2">
              <a v-for="(link, key) in socialLinks" :key="key" :href="link" class="social-link">
                <i :class="'pi pi-' + key + ' text-xl'"></i>
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Footer Bottom Section -->
      <div class="border-t border-gray-700 mt-8 pt-4 text-center text-sm text-[#ccc]">
        <p>&copy; 2025 {{ companyInfoStore.companyInfo?.name }}. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue';
import { useCompanyInfoStore } from '@/store/company';
const companyInfoStore = useCompanyInfoStore();

const formattedAddress = computed(() => {
  const address = companyInfoStore.companyInfo?.address;
  return address ? `${address.street_address}, ${address.city}, ${address.state}, ${address.zip_code}, ${address.country}` : "No address available";
});

const socialLinks = computed(() => {
  return {
    facebook: companyInfoStore.companyInfo?.facebook_link,
    twitter: companyInfoStore.companyInfo?.twitter_link,
    instagram: companyInfoStore.companyInfo?.instagram_link,
    linkedin: companyInfoStore.companyInfo?.linkedin_link
  };
});
</script>

<style scoped>
.bullet-link {
  position: relative;
  padding-left: 24px;
  color: white;
  transition: color 0.3s ease-in-out;
}

.bullet-link::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  width: 6px;
  height: 6px;
  border: 1px solid grey;
  border-radius: 50%;
  transform: translateY(-50%);
  transition: background 0.3s ease-in-out;
}

.bullet-link:hover {
  color: #ffc107;
}

.bullet-link:hover::before {
  background: #ffc107;
}

.social-link {
  color: #ffc107;
  transition: color 0.3s ease-in-out, transform 0.2s ease-in-out;
}

.social-link:hover {
  color: #ff6f00;
  transform: scale(1.2);
}
</style>
