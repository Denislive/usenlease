import { ref } from 'vue';

// Store for notifications
const notifications = ref([]);

const useNotifications = () => {
    // Function to show a notification
    const showNotification = (message, description, type = 'info') => {
        // Push the new notification to the notifications list
        notifications.value.push({ message, description, type });

        // Automatically dismiss the notification after 5 seconds
        setTimeout(() => {
            notifications.value.shift(); // Remove the first notification
        }, 15000); // Notification will disappear after 5 seconds
    };

    // Function to remove a notification manually by index
    const removeNotification = (index) => {
        // Remove notification at the specified index
        notifications.value.splice(index, 1);
    };

    // Return the notifications array and functions to manage them
    return { notifications, showNotification, removeNotification };
};

export default useNotifications;
