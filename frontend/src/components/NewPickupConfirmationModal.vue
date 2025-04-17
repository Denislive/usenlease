<template>
    <!-- Existing template remains unchanged -->
    <transition name="modal" @after-enter="onModalEnter">
      <div v-if="showPickupModal" class="fixed inset-0 bg-[#1c1c1c]/80 flex justify-center items-center z-50">
        <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md animate-pop relative">
          <!-- Modal Header -->
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-bold text-[#1c1c1c]">Confirm Pickup</h3>
            <button
              @click="closePickupModal"
              class="text-[#1c1c1c] hover:text-[#ffc107] transition"
            >
              <i class="pi pi-times text-xl"></i>
            </button>
          </div>
  
          <!-- Webcam Preview -->
          <div class="relative w-full h-64 rounded-lg overflow-hidden border border-gray-200 shadow-sm mb-6">
            <video ref="webcam" class="w-full h-full object-cover" playsinline></video>
            <div v-if="!isWebcamReady" class="absolute inset-0 flex items-center justify-center bg-gray-100">
              <p class="text-gray-500">Camera loading...</p>
            </div>
          </div>
  
          <!-- Capture Image Button -->
          <button
            @click="captureImage"
            class="w-full bg-[#1c1c1c] text-[#ffc107] font-semibold py-3 rounded-lg hover:bg-[#ffc107] hover:text-[#1c1c1c] transition flex items-center justify-center mb-6"
            :disabled="!isWebcamReady"
          >
            <i class="pi pi-camera mr-2"></i>
            Capture ID
          </button>
  
          <!-- Captured Image Preview -->
          <div v-if="capturedImage" class="mb-6">
            <h4 class="text-sm font-medium text-[#1c1c1c] mb-2">Captured Image:</h4>
            <div class="relative w-full h-64 rounded-lg overflow-hidden border border-gray-200">
              <img :src="capturedImage" class="w-full h-full object-cover" alt="Captured ID" />
              <button
                @click="capturedImage = null"
                class="absolute top-2 right-2 bg-[#1c1c1c] text-[#ffc107] rounded-full h-8 w-8 flex items-center justify-center hover:bg-[#ffc107] hover:text-[#1c1c1c] transition"
              >
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </div>
  
          <!-- Action Buttons -->
          <div class="flex justify-end space-x-3">
            <button
              @click="closePickupModal"
              class="px-6 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 transition font-semibold"
            >
              Cancel
            </button>
            <button
              @click="confirmPickup"
              class="px-6 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-lg hover:bg-[#e0a800] transition font-semibold flex items-center"
              :disabled="!capturedImage"
            >
              <i class="pi pi-check mr-2"></i>
              Confirm Pickup
            </button>
          </div>
  
          <!-- Hidden Canvas for Capturing Image -->
          <canvas ref="canvas" class="hidden"></canvas>
        </div>
      </div>
    </transition>
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
      required: true,
    },
  });
  
  const emit = defineEmits(["close", "confirm"]);
  
  const webcam = ref(null);
  const canvas = ref(null);
  const capturedImage = ref(null);
  const isWebcamReady = ref(false);
  let stream = null;
  
  // Clean up webcam on component unmount
  onBeforeUnmount(() => {
    stopWebcam();
  });
  
  // Watch for modal state changes
  watch(
    () => props.showPickupModal,
    (newVal) => {
      if (!newVal) {
        stopWebcam();
        isWebcamReady.value = false;
      }
    }
  );
  
  // Called after modal transition completes
  const onModalEnter = async () => {
    await nextTick();
    await startWebcamWithRetry();
  };
  
  const startWebcamWithRetry = async (retries = 3, delay = 500) => {
    for (let i = 0; i < retries; i++) {
      if (webcam.value) {
        const success = await startWebcam();
        if (success) return;
      }
      console.warn(`Webcam initialization attempt ${i + 1}/${retries} failed, retrying...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    console.error("Webcam initialization failed after retries");
    showNotification("Error", "Unable to initialize camera. Please try again later.", "error");
  };
  
  const startWebcam = async () => {
    if (!webcam.value) {
      console.error("Webcam element not found");
      showNotification("Error", "Camera element not found. Please try again.", "error");
      return false;
    }
  
    try {
      // Check for secure context (HTTPS or localhost)
      if (!window.isSecureContext) {
        showNotification(
          "Error",
          "Camera access requires a secure connection (HTTPS). Please contact support.",
          "error"
        );
        return false;
      }
  
      // Verify browser support
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showNotification(
          "Error",
          "Camera access is not supported in this browser. Please use a modern browser.",
          "error"
        );
        return false;
      }
  
      // Check permission status if Permissions API is available
      let permissionState = "unknown";
      if (navigator.permissions && navigator.permissions.query) {
        try {
          const permissionStatus = await navigator.permissions.query({ name: "camera" });
          permissionState = permissionStatus.state;
  
          if (permissionState === "denied") {
            showNotification(
              "Error",
              "Camera permission was denied. Please enable it in your browser settings and try again.",
              "error"
            );
            return false;
          }
  
          if (permissionState === "granted") {
            isWebcamReady.value = true;
          } else {
            showNotification(
              "Info",
              "Please allow camera access when prompted to proceed.",
              "info"
            );
          }
  
          // Monitor permission changes
          permissionStatus.onchange = () => {
            if (permissionStatus.state === "denied") {
              stopWebcam();
              showNotification(
                "Error",
                "Camera permission was revoked. Please enable it to continue.",
                "error"
              );
            }
          };
        } catch (err) {
          console.warn("Permissions API query failed:", err);
        }
      }
  
      // Check available video devices
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoInputDevices = devices.filter(device => device.kind === "videoinput");
  
      if (videoInputDevices.length === 0) {
        showNotification("Error", "No camera found on this device.", "error");
        return false;
      }
  
      // Request camera access with flexible constraints
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: "environment" },
          width: { ideal: 1280, min: 640 },
          height: { ideal: 720, min: 360 }
        }
      });
  
      if (webcam.value) {
        webcam.value.srcObject = stream;
        await webcam.value.play();
        isWebcamReady.value = true;
        console.log("Webcam initialized successfully");
        return true;
      } else {
        throw new Error("Webcam element became unavailable during initialization");
      }
  
    } catch (err) {
      console.error("Error accessing webcam:", err);
      let message = "Failed to access camera. Please try again.";
      let errorType = "error";
  
      switch (err.name) {
        case "NotAllowedError":
        case "PermissionDeniedError":
          message = "Camera access was denied. Please allow camera permissions in your browser settings.";
          break;
        case "NotFoundError":
        case "DevicesNotFoundError":
          message = "No camera found on this device.";
          break;
        case "OverconstrainedError":
          message = "Camera settings are not supported. Trying fallback settings...";
          errorType = "warning";
          // Attempt fallback with minimal constraints
          return await tryFallbackWebcam();
        case "NotReadableError":
          message = "Camera is in use by another application. Please close it and try again.";
          break;
        case "SecurityError":
          message = "Camera access is blocked due to security settings. Please check your browser configuration.";
          break;
        default:
          console.error("Unhandled webcam error:", err);
      }
  
      showNotification(errorType, message, errorType);
      isWebcamReady.value = false;
      return false;
    }
  };
  
  // Fallback for overconstrained errors
  const tryFallbackWebcam = async () => {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: true // Minimal constraints
      });
  
      if (webcam.value) {
        webcam.value.srcObject = stream;
        await webcam.value.play();
        isWebcamReady.value = true;
        showNotification("Success", "Camera accessed with fallback settings.", "success");
        return true;
      }
      return false;
    } catch (err) {
      console.error("Fallback webcam attempt failed:", err);
      showNotification("Error", "Failed to access camera even with fallback settings.", "error");
      return false;
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
    isWebcamReady.value = false;
  };
  
  const captureImage = () => {
    if (!webcam.value || !canvas.value || !stream || !isWebcamReady.value) {
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
  
  <style scoped>
  .modal-enter-active,
  .modal-leave-active {
    transition: opacity 0.3s ease;
  }
  
  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
  }
  
  .animate-pop {
    animation: pop 0.3s ease-out;
  }
  
  @keyframes pop {
    0% {
      transform: scale(0.95);
      opacity: 0;
    }
    100% {
      transform: scale(1);
      opacity: 1;
    }
  }
  </style>