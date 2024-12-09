<template>
  <div class="mx-auto p-4" v-if="equipment">
    <!-- Main Image with Zoom Effect -->
    <div class="relative overflow-hidden">
      <img
        :src="currentImage ? `${api_base_url}${currentImage}` : placeholderImage"
        alt="Main Equipment Image"
        class="w-full h-128 object-cover rounded-lg shadow-lg"
        @mousemove="zoomImage"
        @mouseleave="resetZoom"
        ref="mainImage"
      />
      <div
        class="zoomed-image"
        v-if="zoomed"
        :style="{ backgroundImage: `url(${api_base_url}${currentImage})`, backgroundPosition: zoomPosition }"
      ></div>
    </div>

    <!-- Carousel Thumbnails -->
    <div class="flex justify-center mt-4">
      <button @click="prevImage" class="text-gray-600 hover:text-gray-800">
        <i class="bi bi-chevron-left"></i>
      </button>
      <div class="flex overflow-x-auto space-x-2">
        <img
          v-for="(image, index) in images"
          :key="index"
          :src="`${api_base_url}${image.image_url}` || placeholderImage"
          alt="Equipment Thumbnail"
          class="w-24 h-24 object-cover rounded-lg cursor-pointer border-2"
          :class="{ 'border-[#ffc107]': currentImage === image.image_url }"
          @click="setCurrentImage(image.image_url)"
        />
      </div>
      <button @click="nextImage" class="text-gray-600 hover:text-gray-800">
        <i class="bi bi-chevron-right"></i>
      </button>
    </div>
  </div>

  <!-- Fallback when equipment is null -->
  <div v-else class="text-center">
    <p>No equipment available.</p>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router'; // Import useRoute to get route params
import axios from 'axios';



export default {
  setup() {
    const placeholderImage = 'https://via.placeholder.com/300x200.png?text=No+Image';
    const equipment = ref(null); // Equipment data to be fetched
    const currentImage = ref(placeholderImage);
    const images = ref([]);
    const zoomed = ref(false);
    const zoomPosition = ref('0%');

    const api_base_url = import.meta.env.VITE_API_BASE_URL;


    // Get the equipment id from the URL
    const route = useRoute();
    const equipmentId = route.params.id; // assuming 'id' is the route parameter

    // Function to fetch equipment data
    const fetchEquipmentData = async () => {
      try {
        const response = await axios.get(`${api_base_url}/api/equipments/${equipmentId}`);
        if (response.data && response.data.images && response.data.images.length > 0) {
          equipment.value = response.data;
          images.value = response.data.images;
          currentImage.value = response.data.images[0].image_url;
        } else {
          equipment.value = null; // Handle case where no images exist
        }
      } catch (error) {
        console.error('Error fetching equipment data:', error);
        equipment.value = null; // Handle error state
      }
    };

    // Fetch equipment data when component is mounted
    onMounted(() => {
      if (equipmentId) {
        fetchEquipmentData();
      }
    });

    // Handle previous and next image changes
    const setCurrentImage = (image) => {
      currentImage.value = image;
    };

    const prevImage = () => {
      const currentIndex = images.value.findIndex(image => image.image_url === currentImage.value);
      const newIndex = (currentIndex - 1 + images.value.length) % images.value.length;
      currentImage.value = images.value.length > 0 ? images.value[newIndex].image_url : placeholderImage;
    };

    const nextImage = () => {
      const currentIndex = images.value.findIndex(image => image.image_url === currentImage.value);
      const newIndex = (currentIndex + 1) % images.value.length;
      currentImage.value = images.value.length > 0 ? images.value[newIndex].image_url : placeholderImage;
    };

    // Zoom effect
    const zoomImage = (event) => {
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

    return {
      api_base_url,
      equipment,
      currentImage,
      images,
      zoomed,
      zoomPosition,
      placeholderImage,
      setCurrentImage,
      prevImage,
      nextImage,
      zoomImage,
      resetZoom,
    };
  },
};
</script>

<style scoped>
.container {
  max-width: 600px;
}

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
}
</style>
