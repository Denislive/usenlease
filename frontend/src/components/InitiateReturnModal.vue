<template>
  <div 
    v-if="isVisible" 
    class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
    role="dialog"
    aria-modal="true"
    aria-labelledby="return-modal-title"
  >
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg mx-4">
      <h2 id="return-modal-title" class="text-2xl font-semibold mb-4 text-center text-gray-800">
        Initiate Return
      </h2>
      <p class="text-md mb-6 text-center text-gray-600">
        Are you sure you want to initiate the return for this item?
      </p>

      <!-- Modal Action Buttons -->
      <div class="flex flex-col sm:flex-row justify-between gap-4">
        <button 
          @click="close" 
          class="w-full py-2 px-4 bg-gray-300 text-gray-800 font-semibold rounded-md hover:bg-gray-400 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          aria-label="Cancel return process"
        >
          Cancel
        </button>
        <button 
          @click="initiateReturn" 
          class="w-full py-2 px-4 bg-[#1c1c1c] text-white font-semibold rounded-md hover:bg-gray-800 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-gray-700 focus:ring-offset-2"
          aria-label="Confirm return process"
        >
          Confirm
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from "vue";
import axios from "axios";
import useNotifications from "@/store/notification.js";
import { useRouter } from "vue-router";

// Constants
const API_ENDPOINT = "/api/order-items/initiate_return/";

// Composables
const { showNotification } = useNotifications();
const router = useRouter();
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

// Props with validation
const props = defineProps({
  isVisible: {
    type: Boolean,
    required: true,
    default: false
  },
  orderItem: {
    type: [String, Number],
    required: true,
    validator: (value) => {
      return value !== null && value !== undefined;
    }
  }
});

// Emits with validation
const emit = defineEmits({
  close: null,
  'return-initiated': null
});

/**
 * Initiates the return process for the order item
 */
const initiateReturn = async () => {
  try {
    if (!props.orderItem) {
      throw new Error("Invalid order item");
    }

    await axios.post(
      `${apiBaseUrl}${API_ENDPOINT}${props.orderItem}/`,
      {},
      { 
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    emit("return-initiated");
    close();
    showNotification({
      title: "Success",
      message: "Return initiated successfully!",
      type: "success"
    });
    router.push('/orders');
    
  } catch (error) {
    console.error("Return initiation failed:", error);
    showNotification({
      title: "Error",
      message: error.response?.data?.message || "Error initiating return. Please try again.",
      type: "error"
    });
  }
};

/**
 * Closes the modal dialog
 */
const close = () => {
  emit("close");
};
</script>