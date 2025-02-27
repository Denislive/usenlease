<template>
    <div v-if="isVisible" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg">
        <h2 class="text-2xl font-semibold mb-4 text-center text-gray-800">Approve Rental</h2>
        <p class="text-md mb-4 text-center text-gray-600">Are you sure you want to approve renting of {{ rental.item.name }}?</p>
        
        <!-- Rental Details Section -->
        <div class="space-y-4 mb-6">
          <p class="text-sm font-medium text-gray-700"><strong>Rental ID:</strong> {{ rental.id }}</p>
          <p class="text-sm font-medium text-gray-700"><strong>Total Price:</strong> ${{ rental.quantity * rental.item.hourly_rate }}</p>
        </div>
  
        <!-- Modal Action Buttons -->
        <div class="flex justify-between space-x-4">
          
          <button 
            @click="close" 
            class="w-full py-2 px-4 bg-gray-300 text-gray-800 font-semibold rounded-md hover:bg-gray-400 transition duration-300"
          >
            Cancel
          </button>
          <button 
            @click="approveRental" 
            class="w-full py-2 px-4 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 transition duration-300"
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
      required: true
    },
    rental: {
      type: Object,
      required: true
    }
  });
  
  const emit = defineEmits(['close', 'approve']);
  
  // Function to approve the rental
  const approveRental = () => {
    emit('approve', props.rental); // Emit the rental object to parent component
    close(); // Close the modal after approval
  };
  
  // Function to close the modal
  const close = () => {
    emit('close'); // Emit an event to close the modal
  };
  </script>
  