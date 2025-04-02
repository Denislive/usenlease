<template>
  <div class="mx-auto p-4" v-if="equipment">
    <!-- Main Image with Zoom Effect -->
    <div class="relative overflow-hidden">
      <div class="relative aspect-square">
        <img
          v-if="currentImage"
          :src="currentImage"
          :alt="equipment.name"
          class="w-full h-full object-cover rounded-lg shadow-lg"
          @mousemove="zoomImage"
          @mouseleave="resetZoom"
          ref="mainImage"
          loading="lazy"
        />
        <div
          v-else
          class="w-full h-full bg-gray-100 flex items-center justify-center rounded-lg"
        >
          <i class="pi pi-image text-8xl text-gray-400"></i>
        </div>
      </div>
      <div
        class="zoomed-image"
        v-if="zoomed && currentImage"
        :style="{ backgroundImage: `url(${currentImage})`, backgroundPosition: zoomPosition }"
      ></div>
    </div>

    <!-- Carousel Thumbnails -->
    <div class="flex justify-center mt-4">
      <button 
        @click="prevImage" 
        class="text-gray-600 hover:text-gray-800"
        :disabled="images.length <= 1"
        aria-label="Previous image"
      >
        <i class="bi bi-chevron-left"></i>
      </button>
      <div class="flex overflow-x-auto space-x-2">
        <div
          v-for="(image, index) in images"
          :key="`thumbnail-${index}`"
          class="w-24 h-24 rounded-lg cursor-pointer border-2 flex-shrink-0"
          :class="{ 'border-[#ffc107]': currentImage === image.image_url }"
          @click="setCurrentImage(image.image_url)"
        >
          <img
            v-if="image.image_url"
            :src="image.image_url"
            :alt="`Thumbnail ${index + 1}`"
            class="w-full h-full object-cover rounded-lg"
            loading="lazy"
            @error="handleImageError(index)"
          />
          <div
            v-else
            class="w-full h-full bg-gray-100 flex items-center justify-center rounded-lg"
          >
            <i class="pi pi-image text-xl text-gray-400"></i>
          </div>
        </div>
      </div>
      <button 
        @click="nextImage" 
        class="text-gray-600 hover:text-gray-800"
        :disabled="images.length <= 1"
        aria-label="Next image"
      >
        <i class="bi bi-chevron-right"></i>
      </button>
    </div>
  </div>

  <!-- Fallback states -->
  <div v-else-if="loading" class="text-center">
    <p>Loading equipment details...</p>
  </div>
  <div v-else class="text-center">
    <p>No equipment available.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import useNotifications from '@/store/notification';

const equipment = ref(null);
const currentImage = ref(null);
const images = ref([]);
const zoomed = ref(false);
const zoomPosition = ref('0%');
const loading = ref(true);
const error = ref(null);

const api_base_url = import.meta.env.VITE_API_BASE_URL;
const { showNotification } = useNotifications();
const route = useRoute();
const equipmentId = route.params.id;

const fetchEquipmentData = async () => {
  if (!equipmentId) {
    error.value = 'No equipment ID provided';
    loading.value = false;
    return;
  }

  try {
    const response = await axios.get(
      `${api_base_url}/api/equipments/${equipmentId}`,
      { timeout: 5000 }
    );
    
    if (response.data?.images?.length > 0) {
      equipment.value = response.data;
      images.value = response.data.images;
      currentImage.value = response.data.images[0].image_url;
    } else {
      equipment.value = response.data;
      images.value = [];
      currentImage.value = null;
    }
  } catch (err) {
    error.value = err;
    showNotification(
      'Error Loading Equipment',
      err.response?.data?.message || err.message || 'Failed to load equipment details',
      'error'
    );
  } finally {
    loading.value = false;
  }
};

const setCurrentImage = (image) => {
  if (!image) return;
  currentImage.value = image;
};

const prevImage = () => {
  if (images.value.length <= 1) return;
  const currentIndex = images.value.findIndex(img => img.image_url === currentImage.value);
  const newIndex = (currentIndex - 1 + images.value.length) % images.value.length;
  currentImage.value = images.value[newIndex].image_url;
};

const nextImage = () => {
  if (images.value.length <= 1) return;
  const currentIndex = images.value.findIndex(img => img.image_url === currentImage.value);
  const newIndex = (currentIndex + 1) % images.value.length;
  currentImage.value = images.value[newIndex].image_url;
};

const zoomImage = (event) => {
  if (!event.target) return;
  
  const { offsetX, offsetY } = event;
  const { clientWidth, clientHeight } = event.target;

  const xPercent = (offsetX / clientWidth) * 100;
  const yPercent = (offsetY / clientHeight) * 100;

  zoomPosition.value = `${xPercent}% ${yPercent}%`;
  zoomed.value = true;
};

const resetZoom = () => {
  zoomed.value = false;
};

const handleImageError = (index) => {
  if (images.value[index]) {
    images.value[index].image_url = null;
  }
  if (currentImage.value === images.value[index]?.image_url) {
    currentImage.value = null;
  }
};

onMounted(() => {
  fetchEquipmentData();
});
</script>

<style scoped>
.zoomed-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: 200%;
  background-repeat: no-repeat;
  background-position: center;
  transition: opacity 0.2s ease;
  pointer-events: none;
  opacity: 1;
  z-index: 10;
}

img {
  transition: transform 0.2s ease;
}

img:hover {
  transform: scale(1.02);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.aspect-square {
  aspect-ratio: 1/1;
}
</style>