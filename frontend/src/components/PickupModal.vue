<template>
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-white rounded-lg shadow-lg w-96 p-4">
            <h2 class="text-xl font-semibold mb-4">Initiate Pickup for Order #{{ order.id }}</h2>

            <!-- Document Selection -->
            <label for="documentType" class="block mb-2">Identity Document Type:</label>
            <select v-model="documentType" id="documentType" class="mb-4 px-4 py-2 border rounded-md w-full">
                <option value="">Select Document Type</option>
                <option value="passport">Passport</option>
                <option value="dl">Driver License</option>
                <option value="id">National ID</option>
            </select>

            <!-- Camera Preview -->
            <div class="mb-4">
                <video ref="videoElement" class="w-full h-auto rounded-md" playsinline autoplay></video>
                <canvas id="canvasElement" class="hidden w-full h-auto"></canvas>
            </div>

            <!-- Capture Image Button -->
            <button @click="captureImage"
                :class="['w-full px-4 py-2 rounded-md shadow-sm', cameraAccessDenied ? 'bg-gray-400 text-gray-800 cursor-not-allowed' : 'bg-[#1c1c1c] text-white hover:bg-[#ffc107] hover:text-[#1c1c1c]']"
                :disabled="cameraAccessDenied">
                Capture Image
            </button>

            <!-- Captured Image Previews -->
            <div class="flex flex-wrap mt-4">
                <div v-for="(image, index) in capturedImages" :key="index"
                    class="relative w-16 h-16 rounded-md overflow-hidden">
                    <img :src="image" alt="Captured Image" class="w-full h-full object-cover p-2" />
                </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-between mt-4">
                <button @click="submitPickup"
                    class="px-4 py-2 bg-[#1c1c1c] text-white rounded-md shadow-sm hover:bg-[#ffc107] hover:text-[#1c1c1c]">
                    Submit Pickup
                </button>
                <button @click="close"
                    class="px-4 py-2 bg-gray-300 text-gray-800 rounded-md shadow-sm hover:bg-gray-400">
                    Cancel
                </button>
            </div>
        </div>
    </div>
</template>
<script>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import useNotifications from "@/store/notification.js"; // Import the notification service
const { showNotification } = useNotifications(); // Initialize notification service


export default {
    props: {
        order: {
            type: Object,
            required: true,
        },
    },
    emits: ['close'],
    setup(props, { emit }) {
        const documentType = ref('');
        const capturedImages = ref([]);
        const cameraAccessDenied = ref(false);
        const cameraStream = ref(null);
        const videoElement = ref(null); // Ref for the video element

        const api_base_url = import.meta.env.VITE_API_BASE_URL;


        // Camera stream reference

        // Start Camera
        const startCamera = async () => {
            console.log("Starting camera...");
            try {
                // Request camera with environment facing mode
                cameraStream.value = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
                console.log("Camera access granted.");

                // Ensure the video element exists
                const video = videoElement.value;
                if (video && video instanceof HTMLVideoElement) {
                    // Set the video source to the camera stream
                    video.srcObject = cameraStream.value;
                    video.onloadedmetadata = () => {
                        video.play();
                        console.log("Video stream playing.");
                    };
                    cameraAccessDenied.value = false;
                } else {
                    console.error("Video element not found or invalid.");
                }
            } catch (error) {
                console.error("Error accessing camera:", error);
                cameraAccessDenied.value = true;
                showNotification('Info', 'You will not be able to capture pickup images.', 'info');
            }
        };


        // Stop Camera
        const stopCamera = () => {
            console.log("Stopping camera...");
            if (cameraStream.value) {
                cameraStream.value.getTracks().forEach(track => track.stop());
                cameraStream.value = null;
                console.log("Camera stopped.");
            } else {
                console.warn("No active camera stream found.");
            }
        };

        // Capture Image (Limit to 3 images)
        const captureImage = () => {
            console.log("Attempting to capture image...");
            if (cameraAccessDenied.value) {
                console.warn("Camera access denied. Cannot capture image.");
                return;
            }
            if (capturedImages.value.length >= 3) {
                showNotification('Info', 'You can only upload a maximum of 3 images.', 'info');
                console.warn("Maximum image limit reached.");
                stopCamera();
                return;
            }

            const canvas = document.getElementById("canvasElement");

            if (canvas instanceof HTMLCanvasElement && videoElement.value instanceof HTMLVideoElement) {
                const context = canvas.getContext("2d");
                canvas.width = videoElement.value.videoWidth;
                canvas.height = videoElement.value.videoHeight;

                context.drawImage(videoElement.value, 0, 0, canvas.width, canvas.height);

                const imageData = canvas.toDataURL("image/png");
                capturedImages.value.push(imageData);
                console.log(`Image captured. Total images: ${capturedImages.value.length}`);
            } else {
                console.error("Video or canvas element not found.");
            }
        };
        const submitPickup = async () => {
            console.log("🚀 Submitting pickup...");

            if (!props.order?.id) {
                console.error("❌ Order ID is missing.");
                showNotification("Error", "Invalid order. Please try again.", "error");
                return;
            }

            if (!documentType.value) {
                console.error("❌ Document type is missing.");
                showNotification("Error", "Please select an identity document type.", "error");
                return;
            }

            // Ensure capturedImages is a valid array
            if (!Array.isArray(capturedImages.value) || capturedImages.value.length === 0) {
                console.warn("⚠️ No captured images found.");
                showNotification("Warning", "Please capture at least one pickup image.", "warning");
                return;
            }

            const formData = new FormData();

            // Convert Base64 images to Blobs and append them under the same key ("pickup_images")
            for (let index = 0; index < capturedImages.value.length; index++) {
                const image = capturedImages.value[index];
                try {
                    const response = await fetch(image);
                    const blob = await response.blob();
                    formData.append("pickup_images", blob, `pickup_image_${index}.png`); // Use pickup_images[] as key
                    console.log(`📸 Image ${index + 1} added to FormData.`);
                } catch (err) {
                    console.error(`🚨 Error converting image at index ${index}:`, err);
                }
            }

            formData.append("documentType", documentType.value);
            formData.append("orderId", props.order.id);

            // Debug: Log FormData contents before sending
            console.log("📝 FormData contents:");
            for (let pair of formData.entries()) {
                console.log(pair[0], pair[1]);
            }

            try {
                console.log("📡 Sending request to server...");
                const response = await axios.post(
                    `${api_base_url}/api/orders/${props.order.id}/initiate_pickup/`,
                    formData,
                    {
                        headers: { "Content-Type": "multipart/form-data" },
                        withCredentials: true,
                    }
                );

                console.log("✅ Pickup submitted successfully:", response.data);
                showNotification("Success", "Pickup initiated successfully!", "info");

                close();
            } catch (error) {
                console.error("❌ Error submitting pickup:", error);
                showNotification("Error", "Failed to initiate pickup. Please try again.", "error");
            }
        };


        // Close the modal
        const close = () => {
            stopCamera();
            emit('close');
        };

        // Initialize camera when the modal is mounted
        onMounted(() => {
            startCamera();
        });

        // Stop camera when the modal is unmounted
        onUnmounted(() => {
            stopCamera();
        });

        return {
            documentType,
            capturedImages,
            cameraAccessDenied,
            videoElement,
            captureImage,
            submitPickup,
            close,
        };
    },
};
</script>