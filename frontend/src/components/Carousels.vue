<template>
    <!-- Trending Ads Carousel Section -->
    <section class="trending-ads py-3">
      <div class="container mx-auto">
        <h4 class="text-center mb-3 text-xl font-semibold">Trending Ads</h4>
        <div class="relative">
          <div class="overflow-hidden">
            <div
              class="flex transition-transform duration-500"
              :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
            >
              <div v-for="ad in trendingAds" :key="ad.id" @click="() => { goToDetail(ad.id) }" class="min-w-[calc(50%-1rem)] mx-2">
                <div class="bg-white rounded-lg shadow-lg overflow-hidden">
                  <div class="relative">
                    <span 
                      :class="ad.is_available ? 'bg-green-500' : 'bg-red-500'"
                      class="text-white text-xs px-2 py-1 rounded"
                    >
                      {{ ad.is_available ? 'Available' : 'Unavailable' }}
                    </span>
                    <img 
                      :src="getFullImageUrl(ad.images[0]?.image_url) || placeholderImage" 
                      alt="Ad Image" 
                      class="w-full h-48 object-cover"
                    />
                    <a 
                      href="#" 
                      class="absolute bottom-4 right-4 bg-blue-500 text-white p-2 rounded-full hover:bg-blue-600 transition duration-300"
                    >
                      <i class="bi bi-cart text-xl"></i>
                    </a>
                  </div>
                  <div class="p-4 text-center">
                    <h5 class="text-sm font-semibold">{{ ad.name }}</h5>
                    <p class="text-gray-600">${{ ad.hourly_rate }} / hr</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <button @click="prev" class="absolute top-1/2 left-0 transform -translate-y-1/2 bg-gray-800 text-white p-2 rounded-full hover:bg-gray-700">
            &lt;
          </button>
          <button @click="next" class="absolute top-1/2 right-0 transform -translate-y-1/2 bg-gray-800 text-white p-2 rounded-full hover:bg-gray-700">
            &gt;
          </button>
        </div>
      </div>
    </section>
  
    <!-- Featured Equipments Carousel Section -->
    <section class="featured-equipments py-3">
      <div class="container mx-auto">
        <h4 class="text-center mb-3 text-xl font-semibold">Featured Equipments</h4>
        <div class="relative">
          <div class="overflow-hidden">
            <div
              class="flex transition-transform duration-500"
              :style="{ transform: `translateX(-${featuredIndex * 100}%)` }"
            >
              <div v-for="equipment in featuredEquipments" :key="equipment.id" @click="() => { goToDetail(equipment.id) }" class="min-w-[calc(50%-1rem)] mx-2">
                <div class="bg-white rounded-lg shadow-lg overflow-hidden">
                  <img 
                    :src="getFullImageUrl(equipment.images[0]?.image_url) || placeholderImage" 
                    alt="Equipment Image" 
                    class="w-full h-32 object-cover"
                  />
                  <div class="p-4 text-center">
                    <h5 class="text-lg font-semibold">{{ equipment.name }}</h5>
                    <p class="text-gray-600">${{ equipment.hourly_rate }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <button @click="prevFeatured" class="absolute top-1/2 left-0 transform -translate-y-1/2 bg-gray-800 text-white p-2 rounded-full hover:bg-gray-700">
            &lt;
          </button>
          <button @click="nextFeatured" class="absolute top-1/2 right-0 transform -translate-y-1/2 bg-gray-800 text-white p-2 rounded-full hover:bg-gray-700">
            &gt;
          </button>
        </div>
      </div>
    </section>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  
  const router = useRouter();

  // Reactive variables to hold ads and equipments
  const trendingAds = ref([]);
  const featuredEquipments = ref([]);
  const currentIndex = ref(0);
  const featuredIndex = ref(0);
  
  // Placeholder image in case the actual image is not available
  const placeholderImage = 'https://via.placeholder.com/300x200.png?text=No+Image';
  
  // Function to fetch equipment data from the API
  const fetchEquipments = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/equipments/');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      trendingAds.value = data; // Populate trending ads from the API
      featuredEquipments.value = data; // Populate featured equipments from the API (can be adjusted based on logic)
    } catch (error) {
      console.error('Error fetching equipments:', error);
    }
  };
  
  // Helper function to construct full image URL
  const getFullImageUrl = (imagePath) => {
    return imagePath ? `http://127.0.0.1:8000${imagePath}` : null;
  };


  const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  } else {
    console.error('Equipment ID is missing!'); // Log an error if ID is missing
  }
}
  
  // Navigation functions
  const next = () => {
    currentIndex.value = (currentIndex.value + 1) % Math.ceil(trendingAds.value.length / 2);
  };
  
  const prev = () => {
    currentIndex.value = (currentIndex.value - 1 + Math.ceil(trendingAds.value.length / 2)) % Math.ceil(trendingAds.value.length / 2);
  };
  
  const nextFeatured = () => {
    featuredIndex.value = (featuredIndex.value + 1) % Math.ceil(featuredEquipments.value.length / 2);
  };
  
  const prevFeatured = () => {
    featuredIndex.value = (featuredIndex.value - 1 + Math.ceil(featuredEquipments.value.length / 2)) % Math.ceil(featuredEquipments.value.length / 2);
  };
  
  // Fetch the equipment data when the component mounts
  onMounted(() => {
    fetchEquipments();
  });
  </script>
  
  <style scoped>
  /* Additional styles can go here if needed */
  </style>
  