<template>
  <div class="fixed top-20 right-5 space-y-4">
    <div
      v-for="(notification, index) in notifications"
      :key="index"
      :class="[
        'border-t-4 rounded-b px-4 py-3 shadow-md flex items-start transition-transform duration-300 transform',
        notificationStyles(notification.type)
      ]"
      role="alert"
    >
      <div class="py-2 flex items-center">
        <!-- PrimeVue icon based on notification type -->
        <i :class="['pi mr-4 text-xl', iconClass(notification.type)]"></i>
      </div>
      <div>
        <p class="font-bold">{{ notification.message }}</p>
        <p class="text-sm">{{ notification.description }}</p>
      </div>

        <!-- Close button -->
        <button
          @click="removeNotification(index)"
          class="ml-auto text-xl text-gray-600 hover:text-gray-800"
          aria-label="Close notification"
        >
          <i class="pi pi-times"></i>
        </button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import useNotifications from '@/store/notification.js';

export default {
  setup() {
    const { notifications, removeNotification } = useNotifications();

    // Style classes based on notification type
    const notificationStyles = (type) => {
      switch (type) {
        case 'success':
          return 'bg-teal-100 border-teal-500 text-teal-900';
        case 'error':
          return 'bg-red-100 border-red-500 text-red-900';
        case 'info':
        default:
          return 'bg-blue-100 border-blue-500 text-blue-900';
      }
    };

    // Icon class based on notification type
    const iconClass = (type) => {
      switch (type) {
        case 'success':
          return 'pi-check text-teal-500';
        case 'error':
          return 'pi-exclamation-triangle text-red-500';
        case 'info':
        default:
          return 'pi-info-circle text-blue-500';
      }
    };

    return {
      notifications,
      notificationStyles,
      iconClass,
      removeNotification,
    };
  },
};
</script>

<style scoped>
.fixed {
  max-width: 350px;
}
</style>
