<template>
  <div v-if="showPickupModal" class="fixed inset-0 bg-gray-900 bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-6 rounded-xl shadow-xl w-full max-w-lg relative">
      
      <!-- Modal Header -->
      <h3 class="text-xl font-semibold text-gray-800 text-center mb-4">Confirm Pickup</h3>

      <!-- Webcam Preview -->
      <div class="relative w-full h-64 rounded-lg overflow-hidden border border-gray-300 shadow-sm">
        <video ref="webcam" class="w-full h-full object-cover"></video>
      </div>

      <!-- Capture Image Button -->
      <button @click="captureImage" 
        class="w-full bg-[#1c1c1c] hover:bg-[#ffc107] hover:text-[#1c1c1c] text-white font-medium py-2 mt-4 rounded-lg transition">
        Capture ID
      </button>

      <!-- Captured Image Preview -->
      <div v-if="capturedImage" class="mt-4">
        <h4 class="text-sm text-gray-600 font-medium mb-2">Captured Image:</h4>
        <img :src="capturedImage" class="w-full h-64 object-cover rounded-lg border border-gray-300" />
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-between items-center mt-6">
        <button @click="closePickupModal" 
          class="w-1/2 bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 rounded-lg transition mr-2">
          Cancel
        </button>
        <button @click="confirmPickup" 
          class="w-1/2 bg-[#1c1c1c] hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition">
          Confirm Pickup
        </button>
      </div>

      <!-- Hidden Canvas for Capturing Image -->
      <canvas ref="canvas" class="hidden"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, defineProps, defineEmits } from "vue";
import axios from "axios";
import useNotifications from "@/store/notification.js"; // Import the notification service
const { showNotification } = useNotifications(); // Initialize notification service

const api_base_url = import.meta.env.VITE_API_BASE_URL;

const props = defineProps({
showPickupModal: Boolean,
orderItem: {
  required: true,
},
});
const emit = defineEmits(["close", "confirm"]);


const webcam = ref(null);
const canvas = ref(null);
const capturedImage = ref(null);
let stream = null;

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
  
  const devices = await navigator.mediaDevices.enumerateDevices();
  const videoInputDevices = devices.filter(device => device.kind === "videoinput");

  if (videoInputDevices.length === 0) {
    console.error("No video input devices found.");
    return;
  }

  stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
  
  if (webcam.value) {
    webcam.value.srcObject = stream;
    await webcam.value.play();
  }
} catch (err) {
  console.error("Error accessing webcam:", err.message);
}
};

const stopWebcam = () => {
if (stream) {
  stream.getTracks().forEach((track) => track.stop());
  stream = null;
}
};

const captureImage = () => {
if (!webcam.value || !canvas.value) return;

const context = canvas.value.getContext("2d");
canvas.value.width = webcam.value.videoWidth;
canvas.value.height = webcam.value.videoHeight;

context.drawImage(webcam.value, 0, 0, canvas.value.width, canvas.value.height);

// Convert image to blob for FormData
canvas.value.toBlob((blob) => {
  if (blob) {
    capturedImage.value = URL.createObjectURL(blob);
  }
}, "image/png");
};

const confirmPickup = async () => {
if (!capturedImage.value) {
  alert("Please capture the ID document first.");
  return;
}

try {
  const formData = new FormData();
  const response = await fetch(capturedImage.value);
  const blob = await response.blob();

  formData.append("id_image", blob, "pickup_id_document.png");

  await axios.post(`${api_base_url}/api/order-items/${props.orderItem}/confirm_pickup/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    withCredentials: true,
  });

  emit("confirm", { orderItem: props.orderItem });
  alert("Pickup confirmed successfully!");
  closePickupModal();
} catch (error) {
  console.error("Pickup confirmation failed:", error);
  alert("Error confirming pickup. Please try again.");
}
};


const closePickupModal = () => {
emit("close");
capturedImage.value = null;
stopWebcam();
};
</script>
