<template>
  <!-- Trending Ads Carousel Section -->
  <section class="trending-ads py-8 bg-gray-50" v-if="trendingAds.length > 0">
    <div class="container mx-auto">
      <h4 class="text-center mb-6 text-3xl font-semibold text-gray-800">Trending Ads</h4>
      <div class="relative">
        <div class="overflow-hidden">
          <div
            class="flex transition-transform duration-500"
            :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
          >
            <div v-for="ad in trendingAds" :key="ad.id" @click="() => { goToDetail(ad.id) }" class="min-w-[calc(50%-1rem)] mx-2">
              <div class="bg-white rounded-lg shadow-xl hover:shadow-2xl overflow-hidden transition-shadow duration-300">
                <div class="relative">
                  <span 
                    :class="ad.is_available ? 'bg-green-500' : 'bg-red-500'"
                    class="absolute top-4 left-4 text-white text-xs font-bold px-3 py-1 rounded-full"
                  >
                    {{ ad.is_available ? 'Available' : 'Unavailable' }}
                  </span>
                  <img 
                    :src="getFullImageUrl(ad.images[0]?.image_url) || placeholderImage" 
                    alt="Ad Image" 
                    class="w-full h-48 object-cover rounded-t-lg"
                  />
                  
                </div>
                <div class="p-4 text-center">
                  <h5 class="text-lg font-semibold text-gray-800">{{ ad.name }}</h5>
                  <p class="text-gray-500">${{ ad.hourly_rate }} / hr</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <button @click="prev" class="absolute top-1/2 left-0 transform -translate-y-1/2 text-white p-2 rounded-full  transition duration-300">
          <i class="text-[#1c1c1c] hover:text-[#ffc107] pi pi-arrow-circle-left text-3xl"></i>
        </button>
        <button @click="next" class="absolute top-1/2 right-0 transform -translate-y-1/2 text-white p-2 rounded-full  transition duration-300">
          <i class="text-[#1c1c1c] hover:text-[#ffc107] pi pi-arrow-circle-right text-3xl"></i>
        </button>
      </div>
    </div>
  </section>

  <!-- Featured Equipments Carousel Section -->
  <section class="featured-equipments py-8 bg-gray-50" v-if="featuredEquipments.length > 0">
    <div class="container mx-auto">
      <h4 class="text-center mb-6 text-3xl font-semibold text-gray-800">Featured Equipments</h4>
      <div class="relative">
        <div class="overflow-hidden">
          <div
            class="flex transition-transform duration-500"
            :style="{ transform: `translateX(-${featuredIndex * 100}%)` }"
          >
            <div v-for="equipment in featuredEquipments" :key="equipment.id" @click="() => { goToDetail(equipment.id) }" class="min-w-[calc(50%-1rem)] mx-2">
              <div class="bg-white rounded-lg shadow-xl hover:shadow-2xl overflow-hidden transition-shadow duration-300">
                <img 
                  :src="getFullImageUrl(equipment.images[0]?.image_url) || placeholderImage" 
                  alt="Equipment Image" 
                  class="w-full h-40 object-cover rounded-t-lg"
                />
                <div class="p-4 text-center">
                  <h5 class="text-lg font-semibold text-gray-800">{{ equipment.name }}</h5>
                  <p class="text-gray-500">${{ equipment.hourly_rate }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <button @click="prevFeatured" class="absolute top-1/2 left-0 transform -translate-y-1/2 text-white p-2 rounded-full  transition duration-300">
          <i class="text-[#1c1c1c] hover:text-[#ffc107] pi pi-arrow-circle-left text-3xl"></i>
        </button>
        <button @click="nextFeatured" class="absolute top-1/2 right-0 transform -translate-y-1/2 text-white p-2 rounded-full  transition duration-300">
          <i class="text-[#1c1c1c] hover:text-[#ffc107] pi pi-arrow-circle-right text-3xl"></i>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const api_base_url = import.meta.env.VITE_API_BASE_URL;

const trendingAds = ref([]);
const featuredEquipments = ref([]);
const currentIndex = ref(0);
const featuredIndex = ref(0);

const placeholderImage = 'https://via.placeholder.com/300x200.png?text=No+Image';

const fetchEquipments = async () => {
  try {
    const response = await fetch(`${api_base_url}/api/equipments/`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    
    // Filter data based on trending and featured status
    trendingAds.value = data.filter(ad => ad.is_trending);
    featuredEquipments.value = data.filter(equipment => equipment.is_featured);
  } catch (error) {
    console.error('Error fetching equipment:', error);
  }
};

const getFullImageUrl = (imagePath) => {
  return imagePath ? `${api_base_url}${imagePath}` : null;
};

const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  } else {
    console.error('Equipment ID is missing!');
  }
};

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

onMounted(() => {
  fetchEquipments();
});
</script>

<style scoped>
/* Customize styles for carousel and buttons */
.trending-ads,
.featured-equipments {
  position: relative;
}

button {
  font-size: 1.5rem;
}
</style>
