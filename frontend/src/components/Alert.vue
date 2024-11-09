<template>
    <transition name="fade">
      <div
        v-if="visible"
        :class="`flex items-center p-4 mb-4 text-sm text-white rounded-lg ${typeClasses}`"
        role="alert"
      >
        <span class="mr-2">{{ message }}</span>
        <button
          @click="closeAlert"
          class="ml-auto text-xl font-semibold leading-none focus:outline-none"
        >
          &times;
        </button>
      </div>
    </transition>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  
  const props = defineProps({
    message: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      default: 'info', // Options: 'info', 'success', 'warning', 'error'
    },
    duration: {
      type: Number,
      default: 3000, // Duration in milliseconds (3 seconds default)
    },
  });
  
  const visible = ref(true);
  
  // Function to close the alert
  const closeAlert = () => {
    visible.value = false;
  };
  
  // Computed property for type-based styling
  const typeClasses = computed(() => {
    switch (props.type) {
      case 'success':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-blue-500';
    }
  });
  
  // Auto-close the alert after specified duration
  onMounted(() => {
    setTimeout(closeAlert, props.duration);
  });
  </script>
  
  <style scoped>
  .fade-enter-active, .fade-leave-active {
    transition: opacity 0.5s;
  }
  .fade-enter, .fade-leave-to {
    opacity: 0;
  }
  </style>
  