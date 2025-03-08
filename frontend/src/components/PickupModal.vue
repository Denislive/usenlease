<template>
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-white rounded-lg shadow-lg w-96 p-4">
            <h2 class="text-xl font-semibold mb-4">Initiate Pickup for OrderItem #{{ orderItem }}</h2>

            <!-- Document Selection -->
            <label for="documentType" class="block mb-2">Identity Document Type:</label>
            <select v-model="documentType" id="documentType" class="mb-2 px-4 py-2 border rounded-md w-full">
                <option value="">Select Document Type</option>
                <option value="passport">Passport</option>
                <option value="dl">Driver License</option>
                <option value="id">National ID</option>
            </select>
            <p v-if="!documentType && formSubmitted" class="text-red-500 text-sm mb-4">Document type is required.</p>

            <!-- Camera Preview -->
            <div class="mb-4">
                <video ref="videoElement" class="w-full h-auto rounded-md" playsinline autoplay></video>
                <canvas ref="canvasElement" class="hidden w-full h-auto"></canvas>
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
            <p v-if="capturedImages.length === 0 && formSubmitted" class="text-red-500 text-sm mb-4">At least one image is required.</p>

            <!-- Actions -->
            <div class="flex justify-between mt-4">
                <button @click="submitPickup" :disabled="isSubmitting"
                    class="px-4 py-2 bg-[#1c1c1c] text-white rounded-md shadow-sm hover:bg-[#ffc107] hover:text-[#1c1c1c] disabled:bg-gray-400 disabled:cursor-not-allowed">
                    {{ isSubmitting ? 'Submitting...' : 'Submit Pickup' }}
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
import useNotifications from "@/store/notification.js";
import { useRouter } from 'vue-router';

const { showNotification } = useNotifications();

export default {
    props: {
        orderItem: {
            required: true,
        },
    },
    emits: ['close'],
    setup(props, { emit }) {
        const router = useRouter();
        const documentType = ref('');
        const capturedImages = ref([]);
        const cameraAccessDenied = ref(false);
        const cameraStream = ref(null);
        const videoElement = ref(null);
        const canvasElement = ref(null);
        const api_base_url = import.meta.env.VITE_API_BASE_URL;
        const formSubmitted = ref(false);
        const isSubmitting = ref(false);

        // Start Camera with Retry Logic
        const startCamera = async (retryCount = 3) => {
            try {
                stopCamera(); // Ensure no lingering streams
                cameraStream.value = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });

                if (videoElement.value) {
                    videoElement.value.srcObject = cameraStream.value;
                    videoElement.value.onloadedmetadata = () => videoElement.value.play();
                }

                cameraAccessDenied.value = false;
            } catch (error) {
                if (retryCount > 0) {
                    setTimeout(() => startCamera(retryCount - 1), 1000);
                } else {
                    cameraAccessDenied.value = true;
                    showNotification("Error", "Unable to access the camera. Please try again.", "error");
                }
            }
        };

        // Stop Camera
        const stopCamera = () => {
            if (cameraStream.value) {
                cameraStream.value.getTracks().forEach(track => track.stop());
                cameraStream.value = null;
            }
        };

        // Capture Image (Limit to 3 images)
        const captureImage = () => {
            if (cameraAccessDenied.value || capturedImages.value.length >= 3) return;

            const canvas = canvasElement.value;
            if (canvas && videoElement.value) {
                const context = canvas.getContext("2d");
                canvas.width = videoElement.value.videoWidth;
                canvas.height = videoElement.value.videoHeight;
                context.drawImage(videoElement.value, 0, 0, canvas.width, canvas.height);
                capturedImages.value.push(canvas.toDataURL("image/png"));
            }
        };

        // Submit Pickup
        const submitPickup = async () => {
            formSubmitted.value = true;

            if (!documentType.value || capturedImages.value.length === 0) {
                showNotification("Error", "Please fill all required fields.", "error");
                return;
            }

            isSubmitting.value = true;

            const formData = new FormData();
            capturedImages.value.forEach((image, index) => {
                fetch(image).then(res => res.blob()).then(blob => {
                    formData.append("pickup_images", blob, `pickup_image_${index}.png`);
                });
            });

            formData.append("documentType", documentType.value);
            formData.append("orderId", props.orderItem.id);

            try {
                await axios.post(`${api_base_url}/api/order-items/${props.orderItem}/initiate_pickup/`, formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                    withCredentials: true,
                });
                showNotification("Success", "Pickup initiated successfully!", "success");
                router.push('/');
                emit('close');
            } catch (error) {
                showNotification("Error", "Failed to initiate pickup. Please try again.", "error");
            } finally {
                isSubmitting.value = false;
            }
        };

        // Close the modal
        const close = () => {
            stopCamera();
            emit('close');
        };

        onMounted(startCamera);
        onUnmounted(stopCamera);

        return {
            documentType,
            capturedImages,
            cameraAccessDenied,
            videoElement,
            canvasElement,
            captureImage,
            submitPickup,
            close,
            formSubmitted,
            isSubmitting,
        };
    },
};
</script>