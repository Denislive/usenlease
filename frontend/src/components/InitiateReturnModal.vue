<template>
  <div v-if="isVisible" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg">
      <h2 class="text-2xl font-semibold mb-4 text-center text-gray-800">Initiate Return</h2>
      <p class="text-md mb-6 text-center text-gray-600">
        Are you sure you want to initiate the return this item?
      </p>

      <!-- Modal Action Buttons -->
      <div class="flex justify-between space-x-4">
        <button 
          @click="close" 
          class="w-full py-2 px-4 bg-gray-300 text-gray-800 font-semibold rounded-md hover:bg-gray-400 transition duration-300"
        >
          Cancel
        </button>
        <button 
          @click="initiateReturn" 
          class="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 transition duration-300"
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
import useNotifications from "@/store/notification.js"; // Import the notification service
import { useRouter } from "vue-router";

const { showNotification } = useNotifications(); // Initialize notification service
const router = useRouter();
const api_base_url = import.meta.env.VITE_API_BASE_URL;

const props = defineProps({
  isVisible: {
    type: Boolean,
    required: true,
  },
  orderItem: {
    required: true,
  },
});

const emit = defineEmits(["close", "return-initiated"]);

// Function to initiate return
const initiateReturn = async () => {
  try {
    await axios.post(
      `${api_base_url}/api/order-items/${props.orderItem}/initiate_return/`,
      {}, // Empty request body
      { withCredentials: true } // Correct placement of withCredentials
    );

    emit("return-initiated"); // Notify parent component
    close();
    showNotification("Success", "Return initiated successfully!", "success");
    router.push('/');
    
  } catch (error) {
    showNotification("Error", "Error initiating return. Please try again.", "error");
  }
};


// Function to close the modal
const close = () => {
  emit("close");
};
</script>
