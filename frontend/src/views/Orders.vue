<template>
  <div class="mx-auto space-y-6 px-4 sm:px-6 lg:px-8">
    <!-- Header Section -->
    <div
      class="max-w-4xl mx-auto bg-gradient-to-r from-amber-400 to-amber-600 text-[#1c1c1c] rounded-2xl shadow-xl p-4 sm:p-6 lg:p-8 text-center">
      <h2 class="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-extrabold tracking-wide">Item Manager</h2>
      <p class="mt-2 text-xs sm:text-sm md:text-base text-[#1c1c1c]/80">Effortlessly manage your items and track rentals.</p>
    </div>

    <!-- Filters Section -->
    <div class="mx-auto flex flex-col sm:flex-row gap-3 sm:gap-4 mb-6 justify-center items-center">
      <select v-model="selectedStatus" @change="filterOrders"
        class="px-3 py-1.5 sm:px-4 sm:py-2 bg-white border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-auto text-xs sm:text-sm md:text-base"
        aria-label="Filter orders by status">
        <option value="">All Statuses</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rented">Rented</option>
        <option value="pickup">Pickup Initiated</option>
        <option value="return">Return Initiated</option>
        <option value="rejected">Rejected</option>
        <option value="canceled">Canceled</option>
        <option value="completed">Completed</option>
        <option value="returned">Returned</option>
        <option value="partially_returned">Partially Returned</option>
      </select>
      <input v-model="searchQuery" @input="filterOrders" type="text" placeholder="Search by Order ID"
        class="px-3 py-1.5 sm:px-4 sm:py-2 bg-white border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-auto text-xs sm:text-sm md:text-base"
        aria-label="Search orders by ID" />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center text-gray-600 text-xs sm:text-sm md:text-base">Loading orders...</div>

    <!-- Orders Table -->
    
    <div v-else class="overflow-x-auto p-2 bg-white rounded-lg shadow">
  <table class="overflow-x-auto min-w-full bg-white border-collapse border-gray-300 whitespace-nowrap">

        <thead class="overflow-x-auto">
          <tr class="bg-gray-200 text-gray-600 uppercase text-xs sm:text-sm">
            <th class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-left hidden sm:table-cell">Order ID</th>
            <th class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center hidden sm:table-cell">Date</th>
            <th class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center hidden sm:table-cell">Status</th>
            <th class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center">Order Items</th>
            <th class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center hidden md:table-cell">Total Items</th>
            <th class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center hidden md:table-cell">Total Price</th>
            <th class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center">Actions</th>
          </tr>
        </thead>
        <tbody v-if="filteredOrders.length > 0" class="overflow-x-auto text-gray-600 text-xs sm:text-sm">
          <tr v-for="order in filteredOrders" :key="order.id" class="border-b hover:bg-gray-50 transition sm:table-row">
            <td class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center align-middle hidden sm:table-cell">
  {{ order.id }}
</td>

            <td class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center align-middle hidden sm:table-cell">
             {{ formatDate(order.date_created) }}
            </td>
            <td class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center align-middle hidden sm:table-cell">
              <span :class="getStatusStyles(order.status)" class="px-2 sm:px-3 py-1 rounded-full capitalize inline-block">
                {{ order.status.replace('_', ' ') }}
              </span>
            </td>
            <td class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center align-middle">
              <div v-for="item in order.order_items" :key="item.id"
                class="flex flex-col sm:flex-row items-center justify-between py-2 border-b last:border-b-0">
                <div class="flex items-center flex-col sm:flex-row text-center sm:text-left">
                  <img v-if="item.item.images?.length" :src="apiBaseUrl + item.item.images[0].image_url"
                    alt="Item image" class="w-8 h-8 sm:w-10 lg:w-12 sm:h-10 lg:h-12 rounded-full object-cover mb-2 sm:mb-0 sm:mr-2" />
                  <span v-else class="text-gray-500 mb-2 sm:mb-0 sm:mr-2 text-xs sm:text-sm">No image</span>
                  <div>
                    <span class="text-xs sm:text-sm">{{ item.quantity }}x {{ item.item.name }}</span>
                    <span :class="getStatusStyles(item.status)"
                      class="ml-0 sm:ml-2 px-1 sm:px-2 py-1 text-xs rounded-full capitalize inline-block">
                      {{ item.status.replace('_', ' ') }}
                    </span>
                  </div>
                </div>
                <div class="flex gap-2 mt-2 sm:mt-0">
                  <button v-if="item.status === 'approved'" @click="openPickupModal(item.id)"
                    class="px-2 sm:px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 transition text-xs sm:text-sm"
                    aria-label="Initiate pickup">
                    Initiate Pickup
                  </button>
                  <button v-if="item.status === 'rented' && isPastEndDate(item.end_date)"
                    @click="openReturnModal(item.id)"
                    class="px-2 sm:px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition text-xs sm:text-sm"
                    aria-label="Initiate return">
                    Initiate Return
                  </button>
                </div>
              </div>
            </td>
            <td class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center align-middle hidden md:table-cell">
              <span class="md:hidden font-semibold">Total Items: </span>{{ order.total_order_items }}
            </td>
            <td class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center align-middle hidden md:table-cell">
              <span class="md:hidden font-semibold">Total Price: </span>${{ order.order_total_price }}
            </td>
            <td class="py-2 sm:py-3 px-3 sm:px-4 lg:px-6 text-center align-middle sm:table-cell">
              <div class="flex gap-2 justify-center">
                <button v-if="['pending', 'approved', 'rented'].includes(order.status)"
                  @click="performAction(order.id, 'terminate')" :disabled="isActionLoading[order.id]"
                  class="px-2 sm:px-3 lg:px-4 py-1 sm:py-2 bg-red-500 text-white rounded hover:bg-red-600 transition text-xs sm:text-sm"
                  :class="{ 'opacity-50 cursor-not-allowed': isActionLoading[order.id] }" aria-label="Terminate order">
                  {{ isActionLoading[order.id] ? 'Terminating...' : 'Terminate' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
        <div v-else class="flex flex-col items-center justify-center mx-auto bg-white rounded-lg shadow-lg p-4 sm:p-6 lg:p-8 text-center">
          <i class="pi pi-box text-3xl sm:text-4xl lg:text-5xl text-[#ffc107] mb-4"></i>
          <p class="text-sm sm:text-base lg:text-lg text-[#1c1c1c]">Nothing rented yet.</p>
          <RouterLink :to="{ name: 'categories' }"
            class="inline-block mt-4 px-3 sm:px-4 lg:px-6 py-1.5 sm:py-2 bg-[#ffc107] text-[#1c1c1c] rounded-md font-semibold hover:bg-[#e0a800] transition text-xs sm:text-sm md:text-base">
            I am looking for...
          </RouterLink>
        </div>
      </table>
    </div>

    <!-- Pickup Modal -->
    <div v-if="showPickupModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-2 sm:px-4">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-[90vw] sm:max-w-md lg:max-w-lg p-4 sm:p-6">
        <h2 class="text-base sm:text-lg lg:text-xl font-semibold mb-3 sm:mb-4">Initiate Pickup for OrderItem #{{ currentItemId }}</h2>
        <label for="documentType" class="block mb-2 text-xs sm:text-sm font-medium text-gray-700">
          Identity Document Type:
        </label>
        <select v-model="documentType" id="documentType"
          class="mb-2 px-3 py-1.5 sm:px-4 sm:py-2 border rounded-md w-full focus:ring-2 focus:ring-[#1c1c1c] focus:border-[#1c1c1c] text-xs sm:text-sm">
          <option value="">Select Document Type</option>
          <option value="passport">Passport</option>
          <option value="dl">Driver License</option>
          <option value="id">National ID</option>
        </select>
        <p v-if="!documentType && formSubmitted" class="text-red-500 text-xs mb-3 sm:mb-4">
          Document type is required.
        </p>
        <div class="mb-3 sm:mb-4 relative">
          <video ref="videoElement" class="w-full h-auto rounded-md border border-gray-300" playsinline autoplay muted></video>
          <canvas ref="canvasElement" class="hidden"></canvas>
          <div v-if="cameraAccessDenied"
            class="absolute inset-0 bg-gray-100 flex items-center justify-center text-gray-500 text-xs sm:text-sm">
            Camera access denied
          </div>
        </div>
        <button @click="captureImage" :class="[
          'w-full px-3 sm:px-4 py-1.5 sm:py-2 rounded-md shadow-sm font-medium transition text-xs sm:text-sm',
          cameraAccessDenied || capturedImages.length >= 3
            ? 'bg-gray-400 text-gray-800 cursor-not-allowed'
            : 'bg-[#1c1c1c] text-white hover:bg-[#ffc107] hover:text-[#1c1c1c]'
        ]" :disabled="cameraAccessDenied || capturedImages.length >= 3">
          {{ capturedImages.length >= 3 ? 'Maximum 3 images' : 'Capture Image' }}
        </button>
        <div class="mt-3 sm:mt-4">
          <h3 class="text-xs sm:text-sm font-medium text-gray-700 mb-2">
            Captured Images ({{ capturedImages.length }}/3):
          </h3>
          <div class="flex flex-wrap gap-2">
            <div v-for="(image, index) in capturedImages" :key="index"
              class="relative w-14 h-14 sm:w-16 sm:h-16 rounded-md overflow-hidden border border-gray-200">
              <img :src="image" :alt="`Captured document image ${index + 1}`" class="w-full h-full object-cover" />
              <button @click.stop="removeImage(index)"
                class="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                ×
              </button>
            </div>
          </div>
        </div>
        <p v-if="capturedImages.length === 0 && formSubmitted" class="text-red-500 text-xs mb-3 sm:mb-4">
          At least one image is required.
        </p>
        <div class="flex flex-col sm:flex-row justify-between mt-4 sm:mt-6 gap-2 sm:gap-3">
          <button @click="submitPickup" :disabled="isSubmitting" :class="[
            'flex-1 px-3 sm:px-4 py-1.5 sm:py-2 rounded-md shadow-sm font-medium transition text-xs sm:text-sm',
            isSubmitting
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-[#1c1c1c] text-white hover:bg-[#ffc107] hover:text-[#1c1c1c]'
          ]">
            {{ isSubmitting ? 'Submitting...' : 'Submit Pickup' }}
          </button>
          <button @click="handlePickupClose"
            class="flex-1 px-3 sm:px-4 py-1.5 sm:py-2 bg-gray-300 text-gray-800 rounded-md shadow-sm font-medium hover:bg-gray-400 transition text-xs sm:text-sm">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Return Modal -->
    <div v-if="showReturnModal" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 px-2 sm:px-4"
      role="dialog" aria-modal="true" aria-labelledby="return-modal-title">
      <div class="bg-white p-4 sm:p-6 rounded-lg shadow-lg w-full max-w-[90vw] sm:max-w-md lg:max-w-lg">
        <h2 id="return-modal-title" class="text-base sm:text-lg lg:text-xl font-semibold mb-3 sm:mb-4 text-center text-gray-800">
          Initiate Return
        </h2>
        <p class="text-xs sm:text-sm lg:text-md mb-4 sm:mb-6 text-center text-gray-600">
          Are you sure you want to initiate the return for this item?
        </p>
        <div class="flex flex-col sm:flex-row justify-between gap-2 sm:gap-4">
          <button @click="closeReturnModal"
            class="w-full py-1.5 sm:py-2 px-3 sm:px-4 bg-gray-300 text-gray-800 font-semibold rounded-md hover:bg-gray-400 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 text-xs sm:text-sm"
            aria-label="Cancel return process">
            Cancel
          </button>
          <button @click="initiateReturn" :disabled="isActionLoading[currentItemId]"
            class="w-full py-1.5 sm:py-2 px-3 sm:px-4 bg-[#1c1c1c] text-white font-semibold rounded-md hover:bg-gray-800 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-gray-700 focus:ring-offset-2 text-xs sm:text-sm"
            aria-label="Confirm return process">
            {{ isActionLoading[currentItemId] ? 'Processing...' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import { format } from 'date-fns';
import { debounce } from 'lodash';
import useNotifications from '@/store/notification.js';
import { useRouter } from 'vue-router';

const { showNotification } = useNotifications();
const router = useRouter();
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

const orders = ref([]);
const filteredOrders = ref([]);
const searchQuery = ref('');
const selectedStatus = ref('');
const loading = ref(true);
const showPickupModal = ref(false);
const showReturnModal = ref(false);
const currentItemId = ref(null);
const isActionLoading = ref({});

// Pickup Modal State
const documentType = ref('');
const capturedImages = ref([]);
const cameraAccessDenied = ref(false);
const cameraStream = ref(null);
const videoElement = ref(null);
const canvasElement = ref(null);
const formSubmitted = ref(false);
const isSubmitting = ref(false);

// Fetch orders on mount
const fetchOrders = async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/api/orders/`, {
      withCredentials: true,
    });
    orders.value = response.data;
    filteredOrders.value = response.data;
    filterOrders();
  } catch (error) {
    console.error('Error fetching orders:', error);
    showNotification('Error', 'Failed to load orders. Please try again.', 'error');
    filteredOrders.value = orders.value;
  } finally {
    loading.value = false;
  }
};

// Filter orders
const filterOrders = debounce(() => {
  filteredOrders.value = orders.value.filter((order) => {
    return (
      (selectedStatus.value ? order.status === selectedStatus.value : true) &&
      (searchQuery.value
        ? order.id.toString().toLowerCase().includes(searchQuery.value.toLowerCase())
        : true)
    );
  });
}, 300);

// Format date
const formatDate = (date) => {
  try {
    return format(new Date(date), 'Ppp');
  } catch (error) {
    return 'Invalid Date';
  }
};

// Status styles
const getStatusStyles = (status) => ({
  'px-3 py-1 rounded-full text-xs capitalize': true,
  'bg-yellow-200 text-yellow-800': status === 'pending',
  'bg-green-200 text-green-800': status === 'pickup',
  'bg-blue-200 text-blue-800': status === 'approved',
  'bg-orange-200 text-orange-800': status === 'return',
  'bg-green-300 text-green-800': status === 'rented',
  'bg-red-200 text-red-800': status === 'rejected',
  'bg-gray-200 text-gray-800': status === 'canceled',
  'bg-gray-300 text-gray-800': status === 'completed',
  'bg-purple-200 text-purple-800': status === 'returned',
  'bg-indigo-200 text-indigo-800': status === 'partially_returned',
  'bg-red-300 text-red-800': status === 'disputed',
});

// Check if end date is past
const isPastEndDate = (endDate) => {
  try {
    const date = new Date(endDate);
    if (isNaN(date.getTime())) return false;
    return date < new Date();
  } catch (error) {
    return false;
  }
};

// Perform actions (terminate, reorder)
const performAction = async (orderId, action) => {
  isActionLoading.value[orderId] = true;
  try {
    const response = await axios.post(
      `${apiBaseUrl}/api/orders/${orderId}/${action}/`,
      {},
      { withCredentials: true }
    );
    showNotification('Success', `Order ${action}d successfully!`, 'success');
    await fetchOrders();
  } catch (error) {
    console.error(`Error performing ${action}:`, error);
    showNotification('Error', error.response?.data?.error || `Failed to ${action} order.`, 'error');
  } finally {
    isActionLoading.value[orderId] = false;
  }
};

// Pickup Modal Handlers
const startCamera = async (retryCount = 3) => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Camera API not supported');
    }
    stopCamera();
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment',
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
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
      showNotification('Error', 'Camera access denied. Please check permissions and try again.', 'error');
    }
  }
};

const stopCamera = () => {
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach((track) => track.stop());
    cameraStream.value = null;
  }
  if (videoElement.value && videoElement.value.srcObject) {
    videoElement.value.srcObject = null;
  }
};

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
    showNotification('Error', 'Failed to capture image. Please try again.', 'error');
  }
};

const removeImage = (index) => {
  capturedImages.value.splice(index, 1);
};

const submitPickup = async () => {
  formSubmitted.value = true;
  if (!documentType.value) {
    showNotification('Error', 'Please select a document type.', 'error');
    return;
  }
  if (capturedImages.value.length === 0) {
    showNotification('Error', 'Please capture at least one image.', 'error');
    return;
  }
  isSubmitting.value = true;
  try {
    const formData = new FormData();
    const imageBlobs = await Promise.all(
      capturedImages.value.map(async (image, index) => {
        const response = await fetch(image);
        if (!response.ok) throw new Error('Failed to process image');
        return await response.blob();
      })
    );
    imageBlobs.forEach((blob, index) => {
      formData.append('pickup_images', blob, `pickup_image_${index}.jpg`);
    });
    formData.append('documentType', documentType.value);
    formData.append('order_item_id', currentItemId.value);
    await axios.post(
      `${apiBaseUrl}/api/order-items/${currentItemId.value}/initiate_pickup/`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        withCredentials: true,
      }
    );
    showNotification('Success', 'Pickup initiated successfully!', 'success');
    handlePickupClose();
  } catch (error) {
    console.error('Submission error:', error);
    showNotification('Error', error.response?.data?.message || 'Failed to initiate pickup. Please try again.', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

const openPickupModal = (itemId) => {
  currentItemId.value = itemId;
  showPickupModal.value = true;
  documentType.value = '';
  capturedImages.value = [];
  formSubmitted.value = false;
  isSubmitting.value = false;
  cameraAccessDenied.value = false;
  startCamera();
};

const handlePickupClose = async () => {
  stopCamera();
  showPickupModal.value = false;
  currentItemId.value = null;
  capturedImages.value = [];
  documentType.value = '';
  await fetchOrders();
};

// Return Modal Handlers
const initiateReturn = async () => {
  if (!currentItemId.value) {
    showNotification('Error', 'Invalid order item.', 'error');
    return;
  }
  isActionLoading.value[currentItemId.value] = true;
  try {
    await axios.post(
      `${apiBaseUrl}/api/order-items/${currentItemId.value}/initiate_return/`,
      {},
      {
        withCredentials: true,
        headers: { 'Content-Type': 'application/json' },
      }
    );
    showNotification('Success', 'Return initiated successfully!', 'success');
    handleReturnInitiated();
  } catch (error) {
    console.error('Return initiation failed:', error);
    showNotification('Error', error.response?.data?.message || 'Error initiating return.', 'error');
  } finally {
    isActionLoading.value[currentItemId.value] = false;
  }
};

const openReturnModal = (itemId) => {
  currentItemId.value = itemId;
  showReturnModal.value = true;
};

const closeReturnModal = () => {
  showReturnModal.value = false;
  currentItemId.value = null;
};

const handleReturnInitiated = async () => {
  closeReturnModal();
  await fetchOrders();
};

// Initialize
onMounted(() => {
  fetchOrders();
});

onUnmounted(() => {
  stopCamera();
});
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  table {
    font-size: 0.875rem;
  }

  th,
  td {
    padding: 0.5rem;
  }
}
</style>