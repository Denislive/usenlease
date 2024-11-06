<template>
  <div class="mx-auto p-4">
    <!-- Main Image with Zoom Effect -->
    <div class="relative overflow-hidden">
      <img
         :src="currentImage ? `http://127.0.0.1:8000${currentImage}` : 'https://picsum.photos/100/150'"
  alt="Main Equipment Image"
        class="w-full h-128 object-cover rounded-lg shadow-lg"
        @mousemove="zoomImage"
        @mouseleave="resetZoom"
        ref="mainImage"
      />
      <div
        class="zoomed-image"
        v-if="zoomed"
        :style="{ backgroundImage: `url(http://127.0.0.1:8000${currentImage})`, backgroundPosition: zoomPosition }"
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
          :src="`http://127.0.0.1:8000${image.image_url}` || placeholderImage" 
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
</template>

<script>
export default {
  props: {
    equipment: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      images: this.equipment?.images || [], // Use optional chaining
      currentImage: (this.equipment?.images[0]?.image_url || this.placeholderImage), // Set to first image or placeholder
      zoomed: false,
      zoomPosition: '0%',
      placeholderImage: 'https://via.placeholder.com/300x200.png?text=No+Image', // Online placeholder image
    };
  },
  watch: {
    equipment: {
      immediate: true,
      handler(newValue) {
        console.log('New equipment prop:', newValue); // Debugging statement
        this.images = newValue?.images || [];
        this.currentImage = (newValue?.images[0]?.image_url || this.placeholderImage);
      },
    },
  },
  methods: {
    setCurrentImage(image) {
      console.log('Setting current image to:', image); // Debugging statement
      this.currentImage = image; // Use selected image
    },
    prevImage() {
      const currentIndex = this.images.findIndex(image => image.image_url === this.currentImage);
      const newIndex = (currentIndex - 1 + this.images.length) % this.images.length;
      this.currentImage = this.images.length > 0 ? this.images[newIndex].image_url : this.placeholderImage;
      console.log('Previous image set to:', this.currentImage); // Debugging statement
    },
    nextImage() {
      const currentIndex = this.images.findIndex(image => image.image_url === this.currentImage);
      const newIndex = (currentIndex + 1) % this.images.length;
      this.currentImage = this.images.length > 0 ? this.images[newIndex].image_url : this.placeholderImage;
      console.log('Next image set to:', this.currentImage); // Debugging statement
    },
    zoomImage(event) {
      const { offsetX, offsetY } = event;
      const { clientWidth, clientHeight } = this.$refs.mainImage;

      // Calculate the percentage position of the mouse within the image
      const xPercent = (offsetX / clientWidth) * 100;
      const yPercent = (offsetY / clientHeight) * 100;

      this.zoomPosition = `${xPercent}% ${yPercent}%`;
      this.zoomed = true;
    },
    resetZoom() {
      this.zoomed = false;
    },
  },
  mounted() {
    console.log('Equipment Image Component Mounted:', this.equipment); // Debugging statement
  },
};
</script>

<style scoped>
.container {
  max-width: 600px; /* Limit the width of the container */
}

.zoomed-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: 200%; /* Adjust size for zoom effect */
  background-repeat: no-repeat;
  background-position: center;
  transition: opacity 0.2s ease;
  pointer-events: none; /* Prevent mouse events on this layer */
  opacity: 1; /* Adjust opacity for visibility */
}
</style>
