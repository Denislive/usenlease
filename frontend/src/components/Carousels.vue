<template>
  <!-- Enhanced Loading State -->
  <div 
    v-if="isLoading"
    class="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-[100] transition-opacity duration-300"
    role="status"
    aria-live="polite"
    aria-label="Loading items"
  >
    <div 
      class="bg-white p-10 rounded-2xl shadow-xl flex flex-col items-center max-w-md mx-4 transform transition-all duration-300 animate-fade-in border border-gray-200"
    >
      <!-- Animated Dots Loader -->
      <div class="flex space-x-2 mb-4">
        <span class="w-3 h-3 bg-[#ff6f00] rounded-full animate-bounce"></span>
        <span class="w-3 h-3 bg-[#ff9e00] rounded-full animate-bounce animation-delay-150"></span>
        <span class="w-3 h-3 bg-[#ffc400] rounded-full animate-bounce animation-delay-300"></span>
      </div>
  
      <!-- Loading text with a subtle animation -->
      <p class="text-sm text-gray-600 tracking-wide font-medium">
        Rent or Lease Anything You Need...
      </p>
    </div>
  </div>
  
  
    <!-- Error State -->
    <div v-if="error" class="container mx-auto p-8 text-center">
      <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
        <div class="flex items-center">
          <i class="pi pi-exclamation-triangle text-red-500 text-2xl mr-3"></i>
          <p class="text-red-700 font-medium">{{ error }}</p>
        </div>
        <button @click="retryFetch" class="mt-3 bg-[#ff6f00] text-white px-4 py-2 rounded hover:bg-[#ff9e00] transition">
          Retry
        </button>
      </div>
    </div>
  
    <!-- Trending Ads Carousel -->
    <section class="trending-ads py-8" v-if="storeTrendingAds.length > 0">
      <div class="container mx-auto px-4">
        <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">Trending Items</h2>
        <div class="relative">
          <div class="overflow-hidden">
            <div class="flex transition-transform duration-300" :style="{ transform: `translateX(-${currentTrendingIndex * 100}%)` }">
              <div 
                v-for="item in storeTrendingAds" 
                :key="item.id" 
                class="flex-shrink-0 w-1/2 sm:w-1/2 md:w-1/3 lg:w-1/4 px-3"
              >
                <EquipmentCard :item="item" @click="goToDetail(item.id)" />
              </div>
            </div>
          </div>
          <button 
            @click="prevTrending" 
            :disabled="currentTrendingIndex === 0"
            class="carousel-button left-0"
            :class="{ 'opacity-50 cursor-not-allowed': currentTrendingIndex === 0 }"
          >
            <i class="pi pi-chevron-left text-2xl"></i>
          </button>
          <button 
            @click="nextTrending" 
            :disabled="currentTrendingIndex >= Math.ceil(storeTrendingAds.length / itemsPerSlide) - 1"
            class="carousel-button right-0"
            :class="{ 'opacity-50 cursor-not-allowed': currentTrendingIndex >= Math.ceil(storeTrendingAds.length / itemsPerSlide) - 1 }"
          >
            <i class="pi pi-chevron-right text-2xl"></i>
          </button>
        </div>
      </div>
    </section>
  
    <!-- Featured Equipment Carousel -->
    <section class="featured-equipments py-8 bg-gray-50" v-if="storeFeaturedEquipments.length > 0">
      <div class="container mx-auto px-4">
        <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">Featured items</h2>
        <div class="relative">
          <div class="overflow-hidden">
            <div class="flex transition-transform duration-300" :style="{ transform: `translateX(-${currentFeaturedIndex * 100}%)` }">
              <div 
                v-for="item in storeFeaturedEquipments" 
                :key="item.id" 
                class="flex-shrink-0 w-1/2 sm:w-1/2 md:w-1/3 lg:w-1/4 px-3"
              >
                <EquipmentCard :item="item" @click="goToDetail(item.id)" />
              </div>
            </div>
          </div>
          <button 
            @click="prevFeatured" 
            :disabled="currentFeaturedIndex === 0"
            class="carousel-button left-0"
            :class="{ 'opacity-50 cursor-not-allowed': currentFeaturedIndex === 0 }"
          >
            <i class="pi pi-chevron-left text-2xl"></i>
          </button>
          <button 
            @click="nextFeatured" 
            :disabled="currentFeaturedIndex >= Math.ceil(storeFeaturedEquipments.length / itemsPerSlide) - 1"
            class="carousel-button right-0"
            :class="{ 'opacity-50 cursor-not-allowed': currentFeaturedIndex >= Math.ceil(storeFeaturedEquipments.length / itemsPerSlide) - 1 }"
          >
            <i class="pi pi-chevron-right text-2xl"></i>
          </button>
        </div>
      </div>
    </section>
  
    <!-- Empty State -->
    <div 
      v-if="!isLoading && !error && storeTrendingAds.length === 0 && storeFeaturedEquipments.length === 0" 
      class="container mx-auto py-16 text-center"
    >
      <div class="max-w-md mx-auto">
        <i class="pi pi-inbox text-6xl text-gray-400 mb-4"></i>
        <h3 class="text-xl font-medium text-gray-600 mb-2">No items available</h3>
        <p class="text-gray-500 mb-6">We couldn't find any trending or featured items at this time.</p>
        <button 
          @click="retryFetch"
          class="bg-[#ff6f00] text-white px-6 py-3 rounded-lg hover:bg-[#ff9e00] transition"
        >
          Refresh List
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { useEquipmentsStore } from '@/store/equipments';
  import EquipmentCard from './EquipmentCard.vue';
  
  const router = useRouter();
  const store = useEquipmentsStore();
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  
  // Responsive items per slide
  const itemsPerSlide = computed(() => {
    if (window.innerWidth < 640) return 2; // Mobile
    if (window.innerWidth < 768) return 2; // Small tablets
    if (window.innerWidth < 1024) return 3; // Tablets
    return 4; // Desktop
  });
  
  const currentTrendingIndex = ref(0);
  const currentFeaturedIndex = ref(0);
  const isLoading = ref(false);
  const error = ref(null);
  
  const storeTrendingAds = computed(() => store.equipments.filter(ad => ad.is_trending));
  const storeFeaturedEquipments = computed(() => store.equipments.filter(equipment => equipment.is_featured));
  
  const retryFetch = () => {
    error.value = null;
    store.fetchEquipments();
  };
  
  const getFullImageUrl = (imagePath) => {
    if (!imagePath) return null;
    return imagePath.startsWith('http') ? imagePath : `${api_base_url}${imagePath}`;
  };
  
  const goToDetail = (equipmentId) => {
    if (!equipmentId) return;
    router.push({ 
      name: 'equipment-details', 
      params: { id: equipmentId }
    });
  };
  
  // Trending carousel navigation
  const nextTrending = () => {
    if (currentTrendingIndex.value < Math.ceil(storeTrendingAds.value.length / itemsPerSlide.value) - 1) {
      currentTrendingIndex.value++;
    }
  };
  
  const prevTrending = () => {
    if (currentTrendingIndex.value > 0) {
      currentTrendingIndex.value--;
    }
  };
  
  // Featured carousel navigation
  const nextFeatured = () => {
    if (currentFeaturedIndex.value < Math.ceil(storeFeaturedEquipments.value.length / itemsPerSlide.value) - 1) {
      currentFeaturedIndex.value++;
    }
  };
  
  const prevFeatured = () => {
    if (currentFeaturedIndex.value > 0) {
      currentFeaturedIndex.value--;
    }
  };
  
  onMounted(() => {
    isLoading.value = true;
    store.fetchEquipments().finally(() => {
      isLoading.value = false;
    });
  
    // Update items per slide on resize
    window.addEventListener('resize', updateItemsPerSlide);
  });
  
  const updateItemsPerSlide = () => {
    // Force recomputation of itemsPerSlide
    itemsPerSlide.value;
  };
  </script>
  
  <style scoped>
  .carousel-button {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.2s ease;
    z-index: 10;
  }
  
  .carousel-button:hover:not(:disabled) {
    background: #f5f5f5;
    transform: translateY(-50%) scale(1.1);
  }
  
  .carousel-button i {
    color: #ff6f00;
  }
  
  @media (max-width: 640px) {
    .flex-shrink-0 {
      width: 50% !important; /* Force 2 items on mobile */
    }
  }
  
  /* Fade-in animation */
  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }
  .animate-fade-in { animation: fadeIn 0.3s ease-out; }
  
  /* Animated dots bouncing */
  @keyframes bounce {
    0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
  }
  .animate-bounce { animation: bounce 1.2s infinite ease-in-out; }
  
  /* Delay animations for a cascading effect */
  .animation-delay-150 { animation-delay: 0.15s; }
  .animation-delay-300 { animation-delay: 0.3s; }
  </style>