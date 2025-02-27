<template>
  <div v-if="showReturnModal" class="fixed inset-0 bg-gray-900 bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-6 rounded-xl shadow-xl w-full max-w-lg relative">
      
      <!-- Modal Header -->
      <h3 class="text-xl font-semibold text-gray-800 text-center mb-4">Confirm Return</h3>

      <!-- Condition Selection -->
      <div class="mb-4">
        <label class="block text-gray-700 font-medium mb-2">Condition of Item:</label>
        <div class="flex space-x-4">
          <label class="flex items-center space-x-2 cursor-pointer">
            <input type="radio" v-model="returnCondition" value="good" class="form-radio text-blue-500">
            <span>Good</span>
          </label>
          <label class="flex items-center space-x-2 cursor-pointer">
            <input type="radio" v-model="returnCondition" value="damaged" class="form-radio text-red-500">
            <span>Damaged</span>
          </label>
        </div>
      </div>

      <!-- Complaint Input Field (Only when "Damaged" is selected) -->
      <div v-if="returnCondition === 'damaged'" class="mb-4">
        <label class="block text-gray-700 font-medium mb-2">Complaint Details (Required):</label>
        <textarea v-model="complaintText" rows="3"
          class="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500"
          placeholder="Describe the issue..."></textarea>
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-between items-center mt-6">
        <button @click="closeReturnModal"
          class="w-1/2 bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 rounded-lg transition mr-2">
          Cancel
        </button>
        <button @click="confirmReturn"
          class="w-1/2 bg-[#1c1c1c] hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition">
          Confirm Return
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch } from "vue";
import useNotifications from "@/store/notification.js"; // Import the notification service
const { showNotification } = useNotifications(); // Initialize notification service

const props = defineProps({
  showReturnModal: Boolean,
  orderItemId: String, // Order item ID for API call
});
const emit = defineEmits(["close", "confirm"]);

const returnCondition = ref("good");
const complaintText = ref("");

// Watch return condition and clear complaint text if "good" is selected
watch(returnCondition, (newValue) => {
  if (newValue === "good") {
    complaintText.value = "";
  }
});

const confirmReturn = () => {
  // Validate if complaint is required but empty
  if (returnCondition.value === "damaged" && !complaintText.value.trim()) {
      showNotification("Error", "Please provide complaint details for damaged items.", "error"); // Notify user
    return;
  }

  // Emit the event with return data
  emit("confirm", {
    returnCondition: returnCondition.value,
    complaintText: returnCondition.value === "damaged" ? complaintText.value : null,
  });

  // Close modal
  closeReturnModal();
};

const closeReturnModal = () => {
  emit("close");
  returnCondition.value = "good";
  complaintText.value = "";
};
</script>
