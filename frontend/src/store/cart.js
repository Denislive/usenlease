import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';
import useNotifications from '@/store/notification.js'; // Import the notification service
import { useRoute } from 'vue-router';
import Cookies from 'js-cookie';

const openIndexedDB = () => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('CartDB', 1);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('cart')) {
                db.createObjectStore('cart', { keyPath: 'id', autoIncrement: true });
            }
        };

        request.onsuccess = (event) => resolve(event.target.result);
        request.onerror = (event) => reject(event.target.error);
    });
};

const getIndexedDBData = async () => {
    const db = await openIndexedDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('cart', 'readonly');
        const store = transaction.objectStore('cart');
        const request = store.getAll();

        request.onsuccess = () => resolve(request.result);
        request.onerror = (event) => reject(event.target.error);
    });
};

const saveIndexedDBData = async (data) => {
    const db = await openIndexedDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('cart', 'readwrite');
        const store = transaction.objectStore('cart');
        store.clear(); // Clear existing data
        data.forEach(item => store.add(item));

        transaction.oncomplete = () => resolve();
        transaction.onerror = (event) => reject(event.target.error);
    });
};

const clearIndexedDBData = async () => {
    const db = await openIndexedDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction('cart', 'readwrite');
        const store = transaction.objectStore('cart');
        const request = store.clear();

        request.onsuccess = () => resolve();
        request.onerror = (event) => reject(event.target.error);
    });
};

export const useCartStore = defineStore('cart', () => {
    const api_base_url = import.meta.env.VITE_API_BASE_URL;

    const cart = ref([]); // Array to hold cart items
    const authStore = useAuthStore();
    axios.defaults.headers.common['X-CSRFToken'] = authStore.getCSRFToken();

    const route = useRoute();
    const { showNotification } = useNotifications(); // Initialize notification service

    // Automatically calculated totals based on cart items
    const cartTotalPrice = computed(() => cart.value.reduce((total, item) => total + parseFloat(item.total), 0));
    const totalCartItems = computed(() => cart.value.length);

    // Load cart based on user's authentication status
    const loadCart = async () => {
        if (authStore.isAuthenticated) {
            try {
                const response = await axios.get(`${api_base_url}/api/cart-items/`, {
                    withCredentials: true,  
                });
                cart.value = response.data;
            } catch (error) {
                showNotification('Error', 'Could not load your cart items.', 'error'); // Show error notification
            }
        } else {
            try {
                cart.value = await getIndexedDBData();
            } catch {
                cart.value = [];
            }
        }
    };

    // Watch the authentication state to load cart data accordingly
    watch(() => authStore.isAuthenticated, loadCart, { immediate: true });

    // Show notification if item not found
    const notifyItemNotFound = () => {
        showNotification('Error', 'Item not found in cart.', 'error');
    };

    // Remove item from the cart
    const removeItem = async (itemId) => {
        const index = cart.value.findIndex(item => item.id === itemId);
        if (index !== -1) {
            cart.value.splice(index, 1); // Remove the item at the found index
            await saveIndexedDBData(cart.value);
        } else {
            notifyItemNotFound();
        }
    };

    // Update item quantity in cart
    const updateItemQuantity = async (itemId, quantity) => {
        const isAuthenticated = authStore.isAuthenticated;
        const foundItem = cart.value.find(item => isAuthenticated ? item.id === itemId : item.item.id === itemId);

        if (!foundItem) {
            notifyItemNotFound();
            return;
        }

        const availableQuantity = isAuthenticated ? foundItem.available_quantity : foundItem.item.available_quantity;

        if (parseInt(quantity) > availableQuantity) {
            showNotification(
                'Quantity Exceeds Availability',
                `Only ${availableQuantity} items are available.`,
                'error'
            );
            return;
        }

        foundItem.quantity = parseInt(quantity);
        foundItem.total = parseFloat(foundItem.hourly_rate) * foundItem.quantity;

        const successMessage = isAuthenticated
            ? `${foundItem.item_details.name} quantity has been updated.`
            : `${foundItem.item.name} quantity has been updated.`;

        showNotification('Quantity Updated', successMessage, 'success');

        if (!isAuthenticated) {
            await saveIndexedDBData(cart.value);
        }
    };

    // Clear the cart
    const clearCart = async () => {
        cart.value = [];
        await clearIndexedDBData();
    };

    const currentCategory = computed(() => route.params.cat || ''); // Retrieve category from URL

    return {
        api_base_url,
        cart,
        currentCategory, // Make category available in the component
        cartTotalPrice,
        totalCartItems,
        removeItem,
        updateItemQuantity,
        clearCart,
        loadCart,
    };
});
