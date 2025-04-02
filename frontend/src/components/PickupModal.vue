<template>
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-lg w-96 p-4">
        <h2 class="text-xl font-semibold mb-4">Initiate Pickup for OrderItem #{{ orderItem }}</h2>
  
        <!-- Document Selection -->
        <label for="documentType" class="block mb-2 text-sm font-medium text-gray-700">
          Identity Document Type:
        </label>
        <select
          v-model="documentType"
          id="documentType"
          class="mb-2 px-4 py-2 border rounded-md w-full focus:ring-2 focus:ring-[#1c1c1c] focus:border-[#1c1c1c]"
        >
          <option value="">Select Document Type</option>
          <option value="passport">Passport</option>
          <option value="dl">Driver License</option>
          <option value="id">National ID</option>
        </select>
        <p v-if="!documentType && formSubmitted" class="text-red-500 text-sm mb-4">
          Document type is required.
        </p>
  
        <!-- Camera Preview -->
        <div class="mb-4 relative">
          <video
            ref="videoElement"
            class="w-full h-auto rounded-md border border-gray-300"
            playsinline
            autoplay
            muted
          ></video>
          <canvas ref="canvasElement" class="hidden"></canvas>
          <div
            v-if="cameraAccessDenied"
            class="absolute inset-0 bg-gray-100 flex items-center justify-center text-gray-500"
          >
            Camera access denied
          </div>
        </div>
  
        <!-- Capture Image Button -->
        <button
          @click="captureImage"
          :class="[
            'w-full px-4 py-2 rounded-md shadow-sm font-medium transition',
            cameraAccessDenied || capturedImages.length >= 3
              ? 'bg-gray-400 text-gray-800 cursor-not-allowed'
              : 'bg-[#1c1c1c] text-white hover:bg-[#ffc107] hover:text-[#1c1c1c]'
          ]"
          :disabled="cameraAccessDenied || capturedImages.length >= 3"
        >
          {{ capturedImages.length >= 3 ? 'Maximum 3 images' : 'Capture Image' }}
        </button>
  
        <!-- Captured Image Previews -->
        <div class="mt-4">
          <h3 class="text-sm font-medium text-gray-700 mb-2">
            Captured Images ({{ capturedImages.length }}/3):
          </h3>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(image, index) in capturedImages"
              :key="index"
              class="relative w-16 h-16 rounded-md overflow-hidden border border-gray-200"
            >
              <img
                :src="image"
                :alt="`Captured document image ${index + 1}`"
                class="w-full h-full object-cover"
              />
              <button
                @click.stop="removeImage(index)"
                class="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center"
              >
                ×
              </button>
            </div>
          </div>
        </div>
        <p v-if="capturedImages.length === 0 && formSubmitted" class="text-red-500 text-sm mb-4">
          At least one image is required.
        </p>
  
        <!-- Actions -->
        <div class="flex justify-between mt-6 gap-3">
          <button
            @click="submitPickup"
            :disabled="isSubmitting"
            :class="[
              'flex-1 px-4 py-2 rounded-md shadow-sm font-medium transition',
              isSubmitting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-[#1c1c1c] text-white hover:bg-[#ffc107] hover:text-[#1c1c1c]'
            ]"
          >
            {{ isSubmitting ? 'Submitting...' : 'Submit Pickup' }}
          </button>
          <button
            @click="close"
            class="flex-1 px-4 py-2 bg-gray-300 text-gray-800 rounded-md shadow-sm font-medium hover:bg-gray-400 transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue';
  import axios from 'axios';
  import useNotifications from "@/store/notification.js";
  import { useRouter } from 'vue-router';
  
  const { showNotification } = useNotifications();
  const router = useRouter();
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  
  const props = defineProps({
    orderItem: {
      type: [Number, String],
      required: true,
    },
  });
  
  const emit = defineEmits(['close']);
  
  // Reactive state
  const documentType = ref('');
  const capturedImages = ref([]);
  const cameraAccessDenied = ref(false);
  const cameraStream = ref(null);
  const videoElement = ref(null);
  const canvasElement = ref(null);
  const formSubmitted = ref(false);
  const isSubmitting = ref(false);
  
  // Camera management
  const startCamera = async (retryCount = 3) => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera API not supported');
      }
  
      stopCamera(); // Clean up any existing stream
  
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
  
      cameraStream.value = stream;
      cameraAccessDenied.value = false;
  
      if (videoElement.value) {
        videoElement.value.srcObject = stream;
      }
    } catch (error) {
      console.error('Camera error:', error);
      if (retryCount > 0) {
        setTimeout(() => startCamera(retryCount - 1), 1000);
      } else {
        cameraAccessDenied.value = true;
        showNotification(
          "Error", 
          "Camera access denied. Please check permissions and try again.", 
          "error"
        );
      }
    }
  };
  
  const stopCamera = () => {
    if (cameraStream.value) {
      cameraStream.value.getTracks().forEach(track => {
        track.stop();
      });
      cameraStream.value = null;
    }
    if (videoElement.value && videoElement.value.srcObject) {
      videoElement.value.srcObject = null;
    }
  };
  
  // Image handling
  const captureImage = () => {
    if (cameraAccessDenied.value || capturedImages.value.length >= 3) return;
  
    try {
      const canvas = canvasElement.value;
      const video = videoElement.value;
  
      if (!canvas || !video || !video.videoWidth || !video.videoHeight) {
        throw new Error('Camera not ready');
      }
  
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
  
      const imageData = canvas.toDataURL('image/jpeg', 0.85);
      capturedImages.value.push(imageData);
    } catch (error) {
      console.error('Error capturing image:', error);
      showNotification("Error", "Failed to capture image. Please try again.", "error");
    }
  };
  
  const removeImage = (index) => {
    capturedImages.value.splice(index, 1);
  };
  
  // Form submission
  const submitPickup = async () => {
    formSubmitted.value = true;
  
    // Validation
    if (!documentType.value) {
      showNotification("Error", "Please select a document type.", "error");
      return;
    }
  
    if (capturedImages.value.length === 0) {
      showNotification("Error", "Please capture at least one image.", "error");
      return;
    }
  
    isSubmitting.value = true;
  
    try {
      const formData = new FormData();
      
      // Process images in parallel
      const imageBlobs = await Promise.all(
        capturedImages.value.map(async (image, index) => {
          const response = await fetch(image);
          if (!response.ok) throw new Error('Failed to process image');
          return await response.blob();
        })
      );
  
      imageBlobs.forEach((blob, index) => {
        formData.append("pickup_images", blob, `pickup_image_${index}.jpg`);
      });
  
      formData.append("document_type", documentType.value);
      formData.append("order_item_id", props.orderItem);
  
      const response = await axios.post(
        `${api_base_url}/api/order-items/${props.orderItem}/initiate_pickup/`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          withCredentials: true,
        }
      );
  
      showNotification("Success", "Pickup initiated successfully!", "success");
      router.push('/');
      close();
    } catch (error) {
      console.error('Submission error:', error);
      const errorMessage = error.response?.data?.message || 
                           "Failed to initiate pickup. Please try again.";
      showNotification("Error", errorMessage, "error");
    } finally {
      isSubmitting.value = false;
    }
  };
  
  const close = () => {
    stopCamera();
    capturedImages.value.forEach(image => URL.revokeObjectURL(image));
    emit('close');
  };
  
  // Lifecycle hooks
  onMounted(() => {
    startCamera();
  });
  
  onUnmounted(() => {
    close();
  });
  </script>