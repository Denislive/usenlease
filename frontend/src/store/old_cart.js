import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';

export const useCartStore = defineStore('cart', () => {
    const cart = ref([]); // Array to hold cart items
    const authStore = useAuthStore();

    // Automatically calculated totals based on cart items
    const cartTotalPrice = computed(() => cart.value.reduce((total, item) => total + parseFloat(item.total), 0));
    const totalCartItems = computed(() => cart.value.reduce((total, item) => total + parseInt(item.quantity), 0));

    // Load cart based on user's authentication status
    const loadCart = async () => {
        if (authStore.isAuthenticated) {
            console.log("Getting cart from database");
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/cart-items/`, {
                    withCredentials: true,
                });
                cart.value = response.data;
                console.log("Cart retrieved from the database:", cart.value);
            } catch (error) {
                console.error("Error getting cart:", error);
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
        }
    };

    const updateItemQuantity = async (itemId, quantity) => {
        console.log(`Attempting to update quantity for item ID: ${itemId}, New quantity: ${quantity}`);
        
        // Find the item in the cart
        const foundItem = cart.value.find(item => item.id === itemId);
        console.log("Found item in cart:", foundItem);
      
        if (foundItem) {
          // Parse and update the quantity
          foundItem.quantity = parseInt(quantity);
          console.log(`Updated quantity for item ID: ${itemId} to ${foundItem.quantity}`);
      
          // Update the total price based on the new quantity
          foundItem.total = parseFloat(foundItem.hourly_rate) * foundItem.quantity;
          console.log(`Updated total for item ID: ${itemId} to ${foundItem.total}`);
        } else {
          console.warn(`Item with ID: ${itemId} not found in cart.`);
        }
      
        console.log("Cart after update:", cart.value);
      };
      
    

    // Clear the cart
    const clearCart = () => {
        cart.value = [];
    };


    return {
        cart,
        cartTotalPrice,
        totalCartItems,
        removeItem,
        updateItemQuantity,
        clearCart,
        loadCart,
    };
});
