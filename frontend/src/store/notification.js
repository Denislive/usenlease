import { ref } from 'vue';

const notifications = ref([]);

const useNotifications = () => {
    const showNotification = (message, description, type = 'info') => {
        notifications.value.push({ message, description, type });
        setTimeout(() => {
            notifications.value.shift();
        }, 5000); // Auto-dismiss notifications after 3 seconds
    };

    const removeNotification = (index) => {
        notifications.value.splice(index, 1); // Remove notification at the specified index
    };

    return { notifications, showNotification, removeNotification };
};

export default useNotifications;
