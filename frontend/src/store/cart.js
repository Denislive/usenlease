import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/store/auth';
import Cookies from 'js-cookie';

export const useCartStore = defineStore('cart', () => {
    const cart = ref([]); // Array to hold cart items
    const cartTotalPrice = computed(() => cart.value.reduce((total, item) => total + item.total, 0));
    const totalCartItems = computed(() => cart.value.reduce((total, item) => total + item.quantity, 0));
    const authStore = useAuthStore();

    // Calculate totals based on cart items
    const calculateTotal = () => {
        cartTotalPrice.value = cart.value.reduce((total, item) => total + item.total, 0);
        totalCartItems.value = cart.value.reduce((total, item) => total + item.quantity, 0);
    };

    // Load cart based on user's authentication status
    const loadCart = () => {
        if (authStore.isAuthenticated) {
            console.log("Getting cart from database");
            // Example API call to load cart data for authenticated users
            // const response = await api.loadCart();
            // cart.value = response.data;
            // calculateTotal();
        } else {
            const savedCart = localStorage.getItem('cart');
            if (savedCart) {
                cart.value = JSON.parse(savedCart);
                calculateTotal(); // Ensure totals are up-to-date
            }
        }
    };

    // Watch the authentication state to load cart data accordingly
    watch(() => authStore.isAuthenticated, () => {
        loadCart(); // Load cart based on updated authentication state
    }, { immediate: true });

    // Add item to the cart
    const addItem = (item) => {
        const foundItem = cart.value.find(cartItem => cartItem.id === item.id);

        if (foundItem) {
            foundItem.quantity += item.quantity;
            foundItem.start_date = item.start_date;
            foundItem.end_date = item.end_date;
            foundItem.total = foundItem.hourly_rate * foundItem.quantity; // Recalculate total
        } else {
            item.total = item.hourly_rate * item.quantity; // Set initial total
            cart.value.push(item);
        }
        calculateTotal();
    };

    // Remove item from the cart
    const removeItem = (itemId) => {
        const index = cart.value.findIndex(item => item.id === itemId);
        if (index !== -1) {
            cart.value.splice(index, 1); // Remove the item at the found index
            calculateTotal();
        }
    };

    // Update item quantity
    const updateItemQuantity = (itemId, quantity) => {
        const foundItem = cart.value.find(item => item.id === itemId);
        if (foundItem) {
            foundItem.quantity = quantity;
            foundItem.total = foundItem.hourly_rate * foundItem.quantity; // Update total based on new quantity
            calculateTotal();
        }
    };

    // Clear the cart
    const clearCart = () => {
        cart.value = [];
        calculateTotal();
    };

    // Save cart to the database or local storage
    const saveCart = async () => {
        if (authStore.isAuthenticated) {
            console.log("Saving cart to database:", cart.value);
            // Example: await api.saveCart(cart.value)
        } else {
            localStorage.setItem('cart', JSON.stringify(cart.value));
        }
    };

    // Automatically save cart changes to persist them
    watch(cart, saveCart, { deep: true });

    return {
        cart,
        cartTotalPrice,
        totalCartItems,
        addItem,
        removeItem,
        updateItemQuantity,
        clearCart,
        loadCart,
    };
});
