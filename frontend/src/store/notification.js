import { ref } from 'vue';

const notifications = ref([]);
const idCounter = ref(0); // For unique IDs

const useNotifications = () => {
  const showNotification = (message, description, type = 'info', duration = 5000) => {
    const id = idCounter.value++;
    const notification = { 
      id, 
      message, 
      description, 
      type,
      duration,
      isLeaving: false // For exit animation
    };
    
    notifications.value.push(notification);

    // Auto-dismiss
    if (duration > 0) {
      setTimeout(() => {
        dismissNotification(id);
      }, duration);
    }
  };

  const dismissNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index !== -1) {
      // Trigger leave animation
      notifications.value[index].isLeaving = true;
      
      // Remove after animation completes
      setTimeout(() => {
        notifications.value = notifications.value.filter(n => n.id !== id);
      }, 300);
    }
  };

  const removeAllNotifications = () => {
    notifications.value = [];
  };

  return { 
    notifications, 
    showNotification, 
    dismissNotification,
    removeAllNotifications
  };
};

export default useNotifications;