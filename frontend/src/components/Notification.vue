<template>
  <div class="fixed top-4 right-4 space-y-2 z-50 max-w-xs w-full">
    <TransitionGroup name="notification">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'border-l-4 rounded-lg px-4 py-3 shadow-lg flex items-start transition-all duration-300',
          'transform hover:scale-[1.02] hover:shadow-xl cursor-pointer',
          notificationStyles(notification.type),
          { 'opacity-0 translate-x-full': notification.isLeaving }
        ]"
        role="alert"
        @click="dismissNotification(notification.id)"
      >
        <div class="flex-shrink-0 pt-0.5">
          <i :class="['pi mr-3 text-xl', iconClass(notification.type)]"></i>
        </div>
        <div class="flex-grow">
          <p class="font-bold">{{ notification.message }}</p>
          <p class="text-sm text-gray-700">{{ notification.description }}</p>
          <div v-if="notification.duration > 0" class="mt-2">
            <div 
              class="h-1 bg-opacity-30 rounded-full overflow-hidden"
              :class="progressBarColor(notification.type)"
            >
              <div
                class="h-full transition-all duration-100 ease-linear"
                :style="{ width: `${notification.progress}%` }"
                :class="progressBarFillColor(notification.type)"
              ></div>
            </div>
          </div>
        </div>
        <button
          @click.stop="dismissNotification(notification.id)"
          class="ml-2 text-gray-500 hover:text-gray-700 focus:outline-none"
          aria-label="Close notification"
        >
          <i class="pi pi-times text-sm"></i>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import useNotifications from '@/store/notification.js';

export default {
  setup() {
    const { notifications, dismissNotification } = useNotifications();
    const intervals = ref({});

    // Start progress tracking for a notification
    const startProgressTracking = (notification) => {
      if (notification.duration <= 0) return;

      const startTime = Date.now();
      notification.progress = 100; // Initialize progress

      intervals.value[notification.id] = setInterval(() => {
        const elapsed = Date.now() - startTime;
        notification.progress = Math.max(0, 100 - (elapsed / notification.duration) * 100);
        
        if (elapsed >= notification.duration) {
          clearInterval(intervals.value[notification.id]);
        }
      }, 50);
    };

    // Clean up intervals
    onMounted(() => {
      notifications.value.forEach(notification => {
        if (notification.duration > 0 && !intervals.value[notification.id]) {
          startProgressTracking(notification);
        }
      });
    });

    onUnmounted(() => {
      Object.values(intervals.value).forEach(interval => clearInterval(interval));
    });

    // Watch for new notifications to start tracking them
    watch(notifications, (newVal) => {
      const lastNotification = newVal[newVal.length - 1];
      if (lastNotification && lastNotification.duration > 0 && !intervals.value[lastNotification.id]) {
        startProgressTracking(lastNotification);
      }
    }, { deep: true });

    // ... rest of your style methods ...
    const notificationStyles = (type) => {
      const styles = {
        success: 'bg-green-50 border-green-500 text-green-800',
        error: 'bg-red-50 border-red-500 text-red-800',
        warning: 'bg-amber-50 border-amber-500 text-amber-800',
        info: 'bg-blue-50 border-blue-500 text-blue-800',
      };
      return styles[type] || styles.info;
    };

    const iconClass = (type) => {
      const icons = {
        success: 'pi-check-circle text-green-500',
        error: 'pi-times-circle text-red-500',
        warning: 'pi-exclamation-circle text-amber-500',
        info: 'pi-info-circle text-blue-500',
      };
      return icons[type] || icons.info;
    };

    const progressBarColor = (type) => {
      const colors = {
        success: 'bg-green-200',
        error: 'bg-red-200',
        warning: 'bg-amber-200',
        info: 'bg-blue-200',
      };
      return colors[type] || colors.info;
    };

    const progressBarFillColor = (type) => {
      const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-amber-500',
        info: 'bg-blue-500',
      };
      return colors[type] || colors.info;
    };

    return {
      notifications,
      dismissNotification,
      notificationStyles,
      iconClass,
      progressBarColor,
      progressBarFillColor,
    };
  },
};
</script>

<style scoped>
.notification-move,
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.notification-leave-active {
  position: absolute;
}
</style>