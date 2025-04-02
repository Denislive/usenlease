<template>
  <div v-if="showPickupModal" class="fixed inset-0 bg-gray-900 bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-6 rounded-xl shadow-xl w-full max-w-lg relative">
      <!-- Modal Header -->
      <h3 class="text-xl font-semibold text-gray-800 text-center mb-4">Confirm Pickup</h3>

      <!-- Webcam Preview -->
      <div class="relative w-full h-64 rounded-lg overflow-hidden border border-gray-300 shadow-sm">
        <video ref="webcam" class="w-full h-full object-cover" playsinline></video>
      </div>

      <!-- Capture Image Button -->
      <button
        @click="captureImage"
        class="w-full bg-[#1c1c1c] hover:bg-[#ffc107] hover:text-[#1c1c1c] text-white font-medium py-2 mt-4 rounded-lg transition"
      >
        Capture ID
      </button>

      <!-- Captured Image Preview -->
      <div v-if="capturedImage" class="mt-4">
        <h4 class="text-sm text-gray-600 font-medium mb-2">Captured Image:</h4>
        <img :src="capturedImage" class="w-full h-64 object-cover rounded-lg border border-gray-300" alt="Captured ID" />
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-between items-center mt-6">
        <button
          @click="closePickupModal"
          class="w-1/2 bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 rounded-lg transition mr-2"
        >
          Cancel
        </button>
        <button
          @click="confirmPickup"
          class="w-1/2 bg-[#1c1c1c] hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition"
        >
          Confirm Pickup
        </button>
      </div>

      <!-- Hidden Canvas for Capturing Image -->
      <canvas ref="canvas" class="hidden"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, defineProps, defineEmits, onBeforeUnmount } from "vue";
import axios from "axios";
import useNotifications from "@/store/notification.js";
const { showNotification } = useNotifications();
import { useRouter } from "vue-router";
const router = useRouter();
const api_base_url = import.meta.env.VITE_API_BASE_URL;

const props = defineProps({
  showPickupModal: Boolean,
  orderItem: {
    type: [Number, String],
    required: true,
  },
});

const emit = defineEmits(["close", "confirm"]);

const webcam = ref(null);
const canvas = ref(null);
const capturedImage = ref(null);
let stream = null;

// Clean up webcam on component unmount
onBeforeUnmount(() => {
  stopWebcam();
});

// Watch for modal state changes
watch(
  () => props.showPickupModal,
  async (newVal) => {
    if (newVal) {
      await nextTick();
      await startWebcam();
    } else {
      stopWebcam();
    }
  }
);

const startWebcam = async () => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error("Webcam access not supported in this browser");
    }

    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoInputDevices = devices.filter(device => device.kind === "videoinput");

    if (videoInputDevices.length === 0) {
      showNotification("Error", "No camera device found.", "error");
      return;
    }

    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "environment",
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    });
    
    if (webcam.value) {
      webcam.value.srcObject = stream;
    }
  } catch (err) {
    console.error("Error accessing webcam:", err);
    showNotification("Error", "Could not access camera. Please check permissions.", "error");
  }
};

const stopWebcam = () => {
  if (stream) {
    stream.getTracks().forEach((track) => {
      track.stop();
    });
    stream = null;
  }
  if (webcam.value && webcam.value.srcObject) {
    webcam.value.srcObject = null;
  }
};

const captureImage = () => {
  if (!webcam.value || !canvas.value || !stream) {
    showNotification("Error", "Camera not ready. Please try again.", "error");
    return;
  }

  try {
    const context = canvas.value.getContext("2d");
    canvas.value.width = webcam.value.videoWidth;
    canvas.value.height = webcam.value.videoHeight;

    context.drawImage(webcam.value, 0, 0, canvas.value.width, canvas.value.height);

    canvas.value.toBlob((blob) => {
      if (blob) {
        capturedImage.value = URL.createObjectURL(blob);
      } else {
        throw new Error("Failed to capture image");
      }
    }, "image/jpeg", 0.9);
  } catch (error) {
    console.error("Error capturing image:", error);
    showNotification("Error", "Failed to capture image. Please try again.", "error");
  }
};

const confirmPickup = async () => {
  if (!capturedImage.value) {
    showNotification("Info", "Please capture the ID document first.", "info");
    return;
  }

  try {
    const response = await fetch(capturedImage.value);
    if (!response.ok) throw new Error("Failed to fetch captured image");
    
    const blob = await response.blob();
    const formData = new FormData();
    formData.append("id_image", blob, "pickup_id_document.jpg");

    await axios.post(
      `${api_base_url}/api/order-items/${props.orderItem}/confirm_pickup/`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
        withCredentials: true,
      }
    );

    emit("confirm", { orderItem: props.orderItem });
    showNotification("Success", "Pickup confirmed successfully!", "success");
    router.push('/');
    closePickupModal();
  } catch (error) {
    console.error("Pickup confirmation error:", error);
    showNotification(
      "Error",
      error.response?.data?.message || "Error confirming pickup. Please try again.",
      "error"
    );
  }
};

const closePickupModal = () => {
  if (capturedImage.value) {
    URL.revokeObjectURL(capturedImage.value);
  }
  capturedImage.value = null;
  stopWebcam();
  emit("close");
};
</script>