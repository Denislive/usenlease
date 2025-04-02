<template>
  <div
    v-if="showReturnModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-50"
    @click.self="closeReturnModal"
  >
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 overflow-hidden">
      <!-- Modal Header -->
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-xl font-semibold text-center text-gray-800">
          Confirm Return
        </h3>
      </div>

      <!-- Modal Content -->
      <div class="p-6">
        <!-- Condition Selection -->
        <div class="mb-6">
          <label class="block text-gray-700 font-medium mb-3">
            Condition of Item:
          </label>
          <div class="grid grid-cols-2 gap-4">
            <label class="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
              :class="{ 'border-blue-500 bg-blue-50': returnCondition === 'good' }">
              <input
                type="radio"
                v-model="returnCondition"
                value="good"
                class="h-5 w-5 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-gray-700">Good</span>
            </label>
            <label class="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
              :class="{ 'border-red-500 bg-red-50': returnCondition === 'damaged' }">
              <input
                type="radio"
                v-model="returnCondition"
                value="damaged"
                class="h-5 w-5 text-red-600 focus:ring-red-500"
              />
              <span class="text-gray-700">Damaged</span>
            </label>
          </div>
        </div>

        <!-- Complaint Input Field -->
        <div v-if="returnCondition === 'damaged'" class="mb-6">
          <label for="complaintDetails" class="block text-gray-700 font-medium mb-2">
            Complaint Details <span class="text-red-500">*</span>
          </label>
          <textarea
            id="complaintDetails"
            v-model="complaintText"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Describe the issue in detail..."
            required
          ></textarea>
          <p v-if="showComplaintError" class="mt-1 text-sm text-red-600">
            Please provide complaint details for damaged items.
          </p>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="flex px-6 py-4 border-t border-gray-200 bg-gray-50">
        <button
          @click="closeReturnModal"
          class="flex-1 mr-3 px-4 py-2 bg-gray-200 text-gray-800 font-medium rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="confirmReturn"
          class="flex-1 px-4 py-2 bg-[#1c1c1c] text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
        >
          Confirm Return
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue';
import useNotifications from '@/store/notification.js';

const { showNotification } = useNotifications();

const props = defineProps({
  showReturnModal: {
    type: Boolean,
    required: true
  },
  orderItemId: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['close', 'confirm']);

// Reactive state
const returnCondition = ref('good');
const complaintText = ref('');
const showComplaintError = ref(false);

// Watch for condition changes
watch(returnCondition, (newValue) => {
  if (newValue === 'good') {
    complaintText.value = '';
    showComplaintError.value = false;
  }
});

const validateForm = () => {
  if (returnCondition.value === 'damaged' && !complaintText.value.trim()) {
    showComplaintError.value = true;
    return false;
  }
  return true;
};

const confirmReturn = () => {
  if (!validateForm()) {
    showNotification(
      'Error',
      'Please provide complaint details for damaged items.',
      'error'
    );
    return;
  }

  emit('confirm', {
    returnCondition: returnCondition.value,
    complaintText: returnCondition.value === 'damaged' ? complaintText.value : null,
    orderItemId: props.orderItemId
  });

  closeReturnModal();
};

const closeReturnModal = () => {
  // Reset form state
  returnCondition.value = 'good';
  complaintText.value = '';
  showComplaintError.value = false;
  
  emit('close');
};
</script>