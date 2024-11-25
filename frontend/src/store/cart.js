import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';
import useNotifications from '@/store/notification.js'; // Import the notification service
import { useRoute } from 'vue-router';
export const useCartStore = defineStore('cart', () => {
    const cart = ref([]); // Array to hold cart items
    const authStore = useAuthStore();
    const route = useRoute();
    const { showNotification } = useNotifications(); // Initialize notification service
    console.log(route)

    // Automatically calculated totals based on cart items
    const cartTotalPrice = computed(() => cart.value.reduce((total, item) => total + parseFloat(item.total), 0));
    const totalCartItems = computed(() => cart.value.length);

    // Load cart based on user's authentication status
    const loadCart = async () => {
        if (authStore.isAuthenticated) {
            console.log("Getting cart from database");
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/cart-items/`, {
                    withCredentials: true,
                });
                cart.value = response.data;
                console.log("Cart retrieved from the database:", cart.value.length);
            } catch (error) {
                console.error("Error getting cart:", error);
                showNotification('Error', 'Could not load your cart items.', 'error'); // Show error notification
            }
        } else {
            const savedCart = localStorage.getItem('cart');
            if (savedCart) {
                cart.value = JSON.parse(savedCart);
            }
        }
    };

    // Watch the authentication state to load cart data accordingly
    watch(() => authStore.isAuthenticated, loadCart, { immediate: true });

    // Remove item from the cart
    const removeItem = (itemId) => {
        const index = cart.value.findIndex(item => item.id === itemId);
        if (index !== -1) {
            cart.value.splice(index, 1); // Remove the item at the found index
            localStorage.setItem('cart', JSON.stringify(cart.value));

            showNotification('Item Removed', 'The item has been removed from your cart.', 'success'); // Show success notification
        } else {
            showNotification('Error', 'Item not found in cart.', 'error'); // Show error notification
        }
    };

    const updateItemQuantity = async (itemId, quantity) => {
        if (authStore.isAuthenticated) {
            const foundItem = cart.value.find(item => item.id === itemId);
            if (foundItem) {
                foundItem.quantity = parseInt(quantity);
                loadCart();
                foundItem.total = parseFloat(foundItem.hourly_rate) * foundItem.quantity;
                showNotification('Quantity Updated', `${foundItem.item_details.name} quantity has been updated.`, 'success');
            } else {
                showNotification('Error', 'Item not found in cart.', 'error');
            }
        } else {
            const foundItem = cart.value.find(item => item.item.id === itemId);
            if (foundItem) {
                foundItem.quantity = parseInt(quantity);
                foundItem.total = parseFloat(foundItem.hourly_rate) * foundItem.quantity;
                loadCart();
                showNotification('Quantity Updated', `${foundItem.item.name} quantity has been updated.`, 'success');
            } else {
                showNotification('Error', 'Item not found in cart.', 'error');
            }
            localStorage.setItem('cart', JSON.stringify(cart.value));
        }
    };

    // Clear the cart
    const clearCart = () => {
        cart.value = [];
        showNotification('Cart Cleared', 'All items have been removed from your cart.', 'success');
    };


    const currentCategory = computed(() => route.params.cat || ''); // Retrieve category from URL


    return {
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
