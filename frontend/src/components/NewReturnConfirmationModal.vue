<template>
  <div
    v-if="showReturnModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-50"
    @click.self="closeReturnModal"
  >
    <div
      class="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 overflow-hidden"
    >
      <!-- Modal Header -->
      <div class="p-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-center text-gray-800">
          Confirm Return
        </h3>
      </div>

      <!-- Modal Content -->
      <div class="p-4">
        <!-- Condition Selection -->
        <div class="mb-4">
          <label class="block text-gray-700 font-medium mb-2">
            Condition of Item:
          </label>
          <div class="grid grid-cols-2 gap-3">
            <label
              class="flex items-center space-x-2 p-2 border rounded-lg cursor-pointer hover:bg-gray-50"
              :class="{ 'border-blue-500 bg-blue-50': returnCondition === 'good' }"
            >
              <input
                type="radio"
                v-model="returnCondition"
                value="good"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-gray-700 text-sm">Good</span>
            </label>
            <label
              class="flex items-center space-x-2 p-2 border rounded-lg cursor-pointer hover:bg-gray-50"
              :class="{ 'border-red-500 bg-red-50': returnCondition === 'damaged' }"
            >
              <input
                type="radio"
                v-model="returnCondition"
                value="damaged"
                class="h-4 w-4 text-red-600 focus:ring-red-500"
              />
              <span class="text-gray-700 text-sm">Damaged</span>
            </label>
          </div>
        </div>

        <!-- Webcam Preview -->
        <div v-if="returnCondition === 'damaged'" class="mb-4">
          <label class="block text-gray-700 font-medium mb-1">
            Capture Item Image
            <span class="text-red-500">*</span>
          </label>
          <div
            class="relative w-full h-48 rounded-lg overflow-hidden border border-gray-200 shadow-sm"
          >
            <video
              ref="webcam"
              class="w-full h-full object-cover"
              playsinline
            ></video>
            <div
              v-if="!isWebcamReady"
              class="absolute inset-0 flex items-center justify-center bg-gray-100"
            >
              <p class="text-gray-500 text-sm">Camera loading...</p>
            </div>
          </div>
          <!-- Capture Image Button -->
          <button
            @click="captureImage"
            class="mt-3 w-full bg-[#1c1c1c] text-white font-semibold py-2 rounded-lg hover:bg-gray-800 transition flex items-center justify-center text-sm"
            :disabled="!isWebcamReady"
          >
            <i class="pi pi-camera mr-2"></i>
            Capture Image
          </button>
          <!-- Captured Image Preview -->
          <div v-if="capturedImage" class="mt-3">
            <h4 class="text-xs font-medium text-gray-700 mb-1">
              Captured Image:
            </h4>
            <div
              class="relative w-full h-48 rounded-lg overflow-hidden border border-gray-200"
            >
              <img
                :src="capturedImage"
                class="w-full h-full object-cover"
                alt="Captured Item"
              />
              <button
                @click="capturedImage = null"
                class="absolute top-1 right-1 bg-[#1c1c1c] text-white rounded-full h-6 w-6 flex items-center justify-center hover:bg-gray-800 transition"
              >
                <i class="pi pi-trash text-xs"></i>
              </button>
            </div>
          </div>
          <p
            v-if="showImageError"
            class="mt-1 text-xs text-red-600"
          >
            Please capture an image of the damaged item.
          </p>
        </div>

        <!-- Complaint Input Field -->
        <div v-if="returnCondition === 'damaged'" class="mb-4">
          <label
            for="complaintDetails"
            class="block text-gray-700 font-medium mb-1"
          >
            Complaint Details
            <span class="text-red-500">*</span>
          </label>
          <textarea
            id="complaintDetails"
            v-model="complaintText"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            placeholder="Describe the issue in detail..."
            required
          ></textarea>
          <p
            v-if="showComplaintError"
            class="mt-1 text-xs text-red-600"
          >
            Please provide complaint details for damaged items.
          </p>
        </div>
      </div>

      <!-- Modal Footer -->
      <div
        class="flex px-4 py-3 border-t border-gray-200 bg-gray-50"
      >
        <button
          @click="closeReturnModal"
          class="flex-1 mr-2 px-3 py-2 bg-gray-200 text-gray-800 font-medium rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors text-sm"
        >
          Cancel
        </button>
        <button
          @click="confirmReturn"
          class="flex-1 px-3 py-2 bg-[#1c1c1c] text-white font-medium rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors text-sm"
        >
          Confirm Return
        </button>
      </div>

      <!-- Hidden Canvas for Capturing Image -->
      <canvas ref="canvas" class="hidden"></canvas>
    </div>
  </div>
</template>
  
  <script setup>
  import {
    ref,
    watch,
    onBeforeUnmount,
    nextTick,
  } from "vue";
  import useNotifications from "@/store/notification.js";
  
  const { showNotification } = useNotifications();
  
  const props = defineProps({
    showReturnModal: {
      type: Boolean,
      required: true,
    },
    orderItemId: {
      required: true,
    },
  });
  
  const emit = defineEmits(["close", "confirm"]);
  
  // Reactive state
  const returnCondition = ref("good");
  const complaintText = ref("");
  const showComplaintError = ref(false);
  const webcam = ref(null);
  const canvas = ref(null);
  const capturedImage = ref(null);
  const isWebcamReady = ref(false);
  const showImageError = ref(false);
  let stream = null;
  
  // Watch for condition changes and modal visibility
  watch(returnCondition, (newValue) => {
    if (newValue === "good") {
      complaintText.value = "";
      showComplaintError.value = false;
      showImageError.value = false;
      if (capturedImage.value) {
        URL.revokeObjectURL(capturedImage.value);
        capturedImage.value = null;
      }
      stopWebcam();
    } else {
      startWebcamWithRetry();
    }
  });
  
  watch(
    () => props.showReturnModal,
    (newVal) => {
      if (newVal && returnCondition.value === "damaged") {
        startWebcamWithRetry();
      } else if (!newVal) {
        stopWebcam();
        resetForm();
      }
    }
  );
  
  // Clean up on component unmount
  onBeforeUnmount(() => {
    stopWebcam();
    if (capturedImage.value) {
      URL.revokeObjectURL(capturedImage.value);
    }
  });
  
  const startWebcamWithRetry = async (
    retries = 3,
    delay = 500
  ) => {
    for (let i = 0; i < retries; i++) {
      if (webcam.value) {
        const success = await startWebcam();
        if (success) return;
      }
      console.warn(
        `Webcam initialization attempt ${i + 1}/${retries} failed, retrying...`
      );
      await new Promise((resolve) =>
        setTimeout(resolve, delay)
      );
    }
    console.error("Webcam initialization failed after retries");
    showNotification(
      "Error",
      "Unable to initialize camera. Please try again later.",
      "error"
    );
  };
  
  const startWebcam = async () => {
    if (!webcam.value) {
      console.error("Webcam element not found");
      showNotification(
        "Error",
        "Camera element not found. Please try again.",
        "error"
      );
      return false;
    }
  
    try {
      // Check secure context
      if (!window.isSecureContext) {
        showNotification(
          "Error",
          "Camera access requires a secure connection (HTTPS). Please contact support.",
          "error"
        );
        return false;
      }
  
      // Verify browser support
      if (
        !navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia
      ) {
        showNotification(
          "Error",
          "Camera access is not supported in this browser. Please use a modern browser.",
          "error"
        );
        return false;
      }
  
      // Check permission status
      let permissionState = "unknown";
      if (
        navigator.permissions &&
        navigator.permissions.query
      ) {
        try {
          const permissionStatus =
            await navigator.permissions.query({
              name: "camera",
            });
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
          console.warn(
            "Permissions API query failed:",
            err
          );
        }
      }
  
      // Check available devices
      const devices =
        await navigator.mediaDevices.enumerateDevices();
      const videoInputDevices = devices.filter(
        (device) => device.kind === "videoinput"
      );
  
      if (videoInputDevices.length === 0) {
        showNotification(
          "Error",
          "No camera found on this device.",
          "error"
        );
        return false;
      }
  
      // Request camera access
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: "environment" },
          width: { ideal: 1280, min: 640 },
          height: { ideal: 720, min: 360 },
        },
      });
  
      if (webcam.value) {
        webcam.value.srcObject = stream;
        await webcam.value.play();
        isWebcamReady.value = true;
        return true;
      } else {
        throw new Error("Webcam element became unavailable");
      }
    } catch (err) {
      console.error("Error accessing webcam:", err);
      let message =
        "Failed to access camera. Please try again.";
      let errorType = "error";
  
      switch (err.name) {
        case "NotAllowedError":
        case "PermissionDeniedError":
          message =
            "Camera access was denied. Please allow camera permissions in your browser settings.";
          break;
        case "NotFoundError":
        case "DevicesNotFoundError":
          message = "No camera found on this device.";
          break;
        case "OverconstrainedError":
          message =
            "Camera settings not supported. Trying fallback settings...";
          errorType = "warning";
          return await tryFallbackWebcam();
        case "NotReadableError":
          message =
            "Camera is in use by another application. Please close it and try again.";
          break;
        case "SecurityError":
          message =
            "Camera access blocked due to security settings. Please check your browser configuration.";
          break;
        default:
          console.error("Unhandled webcam error:", err);
      }
  
      showNotification(errorType, message, errorType);
      isWebcamReady.value = false;
      return false;
    }
  };
  
  const tryFallbackWebcam = async () => {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: true,
      });
  
      if (webcam.value) {
        webcam.value.srcObject = stream;
        await webcam.value.play();
        isWebcamReady.value = true;
        showNotification(
          "Success",
          "Camera accessed with fallback settings.",
          "success"
        );
        return true;
      }
      return false;
    } catch (err) {
      console.error("Fallback webcam attempt failed:", err);
      showNotification(
        "Error",
        "Failed to access camera even with fallback settings.",
        "error"
      );
      return false;
    }
  };
  
  const stopWebcam = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
    if (webcam.value && webcam.value.srcObject) {
      webcam.value.srcObject = null;
    }
    isWebcamReady.value = false;
  };
  
  const captureImage = () => {
    if (
      !webcam.value ||
      !canvas.value ||
      !stream ||
      !isWebcamReady.value
    ) {
      showNotification(
        "Error",
        "Camera not ready. Please try again.",
        "error"
      );
      return;
    }
  
    try {
      const context = canvas.value.getContext("2d");
      canvas.value.width = webcam.value.videoWidth;
      canvas.value.height = webcam.value.videoHeight;
  
      context.drawImage(
        webcam.value,
        0,
        0,
        canvas.value.width,
        canvas.value.height
      );
  
      canvas.value.toBlob(
        (blob) => {
          if (blob) {
            if (capturedImage.value) {
              URL.revokeObjectURL(capturedImage.value);
            }
            capturedImage.value = URL.createObjectURL(blob);
            showImageError.value = false;
          } else {
            throw new Error("Failed to capture image");
          }
        },
        "image/jpeg",
        0.9
      );
    } catch (error) {
      console.error("Error capturing image:", error);
      showNotification(
        "Error",
        "Failed to capture image. Please try again.",
        "error"
      );
    }
  };
  
  const validateForm = () => {
    let isValid = true;
  
    if (returnCondition.value === "damaged") {
      if (!complaintText.value.trim()) {
        showComplaintError.value = true;
        isValid = false;
      } else {
        showComplaintError.value = false;
      }
  
      if (!capturedImage.value) {
        showImageError.value = true;
        isValid = false;
      } else {
        showImageError.value = false;
      }
    }
  
    return isValid;
  };
  
  const confirmReturn = async () => {
    if (!validateForm()) {
      showNotification(
        "Error",
        "Please complete all required fields for damaged items.",
        "error"
      );
      return;
    }
  
    let imageBlob = null;
    if (capturedImage.value) {
      const response = await fetch(capturedImage.value);
      if (response.ok) {
        imageBlob = await response.blob();
      }
    }
  
    emit("confirm", {
      returnCondition: returnCondition.value,
      complaintText:
        returnCondition.value === "damaged"
          ? complaintText.value
          : null,
      orderItemId: props.orderItemId,
      image: imageBlob
        ? { blob: imageBlob, filename: "return_item.jpg" }
        : null,
    });
  
    closeReturnModal();
  };
  
  const closeReturnModal = () => {
    resetForm();
    stopWebcam();
    emit("close");
  };
  
  const resetForm = () => {
    returnCondition.value = "good";
    complaintText.value = "";
    showComplaintError.value = false;
    showImageError.value = false;
    if (capturedImage.value) {
      URL.revokeObjectURL(capturedImage.value);
      capturedImage.value = null;
    }
  };
  </script>