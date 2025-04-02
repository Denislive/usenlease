<template>
  <div
    v-if="isVisible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    @click.self="close"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 overflow-hidden">
      <!-- Modal Header -->
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-2xl font-semibold text-center text-gray-800">
          Approve Rental
        </h2>
        <p class="mt-2 text-center text-gray-600">
          Are you sure you want to approve renting of {{ rental.item.name }}?
        </p>
      </div>

      <!-- Rental Details Section -->
      <div class="p-6 space-y-3 bg-gray-50">
        <div class="flex justify-between">
          <span class="text-sm font-medium text-gray-700">Rental ID:</span>
          <span class="text-sm text-gray-900">{{ rental.id }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-sm font-medium text-gray-700">Quantity:</span>
          <span class="text-sm text-gray-900">{{ rental.quantity }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-sm font-medium text-gray-700">Hourly Rate:</span>
          <span class="text-sm text-gray-900">${{ rental.item.hourly_rate.toFixed(2) }}</span>
        </div>
        <div class="flex justify-between pt-2 border-t border-gray-200">
          <span class="text-sm font-medium text-gray-700">Total Price:</span>
          <span class="text-sm font-semibold text-gray-900">
            ${{ (rental.quantity * rental.item.hourly_rate).toFixed(2) }}
          </span>
        </div>
      </div>

      <!-- Modal Action Buttons -->
      <div class="flex p-4 space-x-4 bg-gray-50">
        <button
          @click="close"
          class="flex-1 px-4 py-2 text-gray-800 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors duration-200"
        >
          Cancel
        </button>
        <button
          @click="approveRental"
          class="flex-1 px-4 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors duration-200"
        >
          Approve
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  isVisible: {
    type: Boolean,
    required: true,
    default: false,
  },
  rental: {
    type: Object,
    required: true,
    validator: (value) => {
      return (
        value &&
        typeof value.id !== 'undefined' &&
        value.item &&
        typeof value.item.name !== 'undefined' &&
        typeof value.item.hourly_rate !== 'undefined' &&
        typeof value.quantity !== 'undefined'
      );
    },
  },
});

const emit = defineEmits(['close', 'approve']);

const approveRental = () => {
  if (!props.rental) {
    console.error('Invalid rental data');
    return;
  }
  emit('approve', props.rental);
  close();
};

const close = () => {
  emit('close');
};
</script>