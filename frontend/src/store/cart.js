import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';
import useNotifications from '@/store/notification.js';
import { useRoute } from 'vue-router';
import Cookies from 'js-cookie';

// Secure IndexedDB operations with error handling
const openIndexedDB = () => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('CartDB', 1);

        request.onupgradeneeded = (event) => {
            try {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('cart')) {
                    db.createObjectStore('cart', { 
                        keyPath: 'id', 
                        autoIncrement: true 
                    });
                }
            } catch (error) {
                console.error('DB upgrade error:', error);
                reject(error);
            }
        };

        request.onsuccess = (event) => {
            resolve(event.target.result);
        };
        
        request.onerror = (event) => {
            console.error('DB open error:', event.target.error);
            reject(event.target.error);
        };
    });
};

const getIndexedDBData = async () => {
    try {
        const db = await openIndexedDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction('cart', 'readonly');
            const store = transaction.objectStore('cart');
            const request = store.getAll();

            request.onsuccess = () => {
                const result = request.result || [];
                resolve(result);
            };
            
            request.onerror = (event) => {
                console.error('DB read error:', event.target.error);
                reject(event.target.error);
            };
        });
    } catch (error) {
        console.error('Failed to get DB data:', error);
        return [];
    }
};

const saveIndexedDBData = async (data) => {
    try {
        const db = await openIndexedDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction('cart', 'readwrite');
            const store = transaction.objectStore('cart');
            
            // Clear existing data first
            const clearRequest = store.clear();

            clearRequest.onsuccess = () => {
                // Add new data with error handling
                const addOperations = data.map(item => {
                    try {
                        // Sanitize data before storing
                        const cleanItem = JSON.parse(JSON.stringify(item));
                        return store.add(cleanItem);
                    } catch (error) {
                        console.error('Data sanitization error:', error);
                        return Promise.reject(error);
                    }
                });

                Promise.all(addOperations)
                    .then(() => resolve())
                    .catch(error => {
                        console.error('DB write error:', error);
                        reject(error);
                    });
            };

            clearRequest.onerror = (event) => {
                console.error('DB clear error:', event.target.error);
                reject(event.target.error);
            };
        });
    } catch (error) {
        console.error('Failed to save DB data:', error);
        throw error;
    }
};

const clearIndexedDBData = async () => {
    try {
        const db = await openIndexedDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction('cart', 'readwrite');
            const store = transaction.objectStore('cart');
            const request = store.clear();

            request.onsuccess = () => resolve();
            request.onerror = (event) => {
                console.error('DB clear error:', event.target.error);
                reject(event.target.error);
            };
        });
    } catch (error) {
        console.error('Failed to clear DB data:', error);
        throw error;
    }
};

export const useCartStore = defineStore('cart', () => {
    const api_base_url = import.meta.env.VITE_API_BASE_URL;
    const cart = ref([]);
    const authStore = useAuthStore();
    const route = useRoute();
    const { showNotification } = useNotifications();

    // Secure computed properties
    const cartTotalPrice = computed(() => {
        return cart.value.reduce((total, item) => {
            const itemTotal = parseFloat(item.total) || 0;
            return total + itemTotal;
        }, 0);
    });

    const totalCartItems = computed(() => cart.value.length);
    const currentCategory = computed(() => route.params.cat || '');

    // Secure cart loading with authentication check
    const loadCart = async () => {
        try {
            if (authStore.isAuthenticated) {
                const response = await axios.get(`${api_base_url}/api/cart-items/`, {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': authStore.getCSRFToken()
                    }
                });
                
                if (response.status === 200) {
                    cart.value = response.data || [];
                } else {
                    throw new Error('Invalid response status');
                }
            } else {
                const dbData = await getIndexedDBData();
                cart.value = Array.isArray(dbData) ? dbData : [];
            }
        } catch (error) {
            console.error('Cart load error:', error);
            cart.value = [];
            showNotification('Error', 'Could not load your cart items.', 'error');
        }
    };

    // Secure authentication state watcher
    watch(() => authStore.isAuthenticated, async (newVal) => {
        try {
            await loadCart();
        } catch (error) {
            console.error('Auth state change error:', error);
        }
    }, { immediate: true });

    // Secure item removal
    const removeItem = async (itemId) => {
        try {
            const index = cart.value.findIndex(item => item.id === itemId);
            if (index === -1) {
                throw new Error('Item not found');
            }

            if (authStore.isAuthenticated) {
                await axios.delete(`${api_base_url}/api/cart-items/${itemId}/`, {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': authStore.getCSRFToken()
                    }
                });
            }

            cart.value.splice(index, 1);
            
            if (!authStore.isAuthenticated) {
                await saveIndexedDBData(cart.value);
            }

            showNotification('Success', 'Item removed from cart', 'success');
        } catch (error) {
            console.error('Remove item error:', error);
            showNotification('Error', 'Failed to remove item from cart', 'error');
        }
    };

    // Secure quantity update with validation
    const updateItemQuantity = async (itemId, quantity) => {
        try {
            quantity = parseInt(quantity, 10);
            if (isNaN(quantity)) {
                throw new Error('Invalid quantity');
            }

            const isAuthenticated = authStore.isAuthenticated;
            const foundItem = cart.value.find(item => 
                isAuthenticated ? item.id === itemId : item.id === itemId
            );

            if (!foundItem) {
                throw new Error('Item not found');
            }

            const availableQuantity = isAuthenticated 
                ? foundItem.available_quantity 
                : foundItem.item?.available_quantity;

            if (quantity <= 0 || quantity > availableQuantity) {
                throw new Error('Invalid quantity');
            }

            foundItem.quantity = quantity;
            foundItem.total = (parseFloat(foundItem.hourly_rate) || 0) * quantity;

            if (isAuthenticated) {
                const payload = {
                    id: foundItem.id,
                    quantity: foundItem.quantity,
                    start_date: foundItem.start_date,
                    end_date: foundItem.end_date,
                    total: foundItem.total,
                };

                await axios.put(`${api_base_url}/api/cart-items/${foundItem.id}/`, 
                    payload, 
                    {
                        withCredentials: true,
                        headers: {
                            'X-CSRFToken': authStore.getCSRFToken()
                        }
                    }
                );
            } else {
                await saveIndexedDBData(cart.value);
            }

            const itemName = isAuthenticated 
                ? foundItem.item_details?.name 
                : foundItem.item?.name;
                
            showNotification(
                'Success', 
                `${itemName || 'Item'} quantity updated`, 
                'success'
            );
        } catch (error) {
            console.error('Quantity update error:', error);
            showNotification(
                'Error', 
                error.message === 'Invalid quantity' 
                    ? 'Please enter a valid quantity' 
                    : 'Failed to update quantity',
                'error'
            );
        }
    };

    // Secure cart clearing
    const clearCart = async () => {
        try {
            if (authStore.isAuthenticated) {
                await axios.delete(`${api_base_url}/api/cart-items/clear/`, {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': authStore.getCSRFToken()
                    }
                });
            } else {
                await clearIndexedDBData();
            }
            
            cart.value = [];
            showNotification('Success', 'Cart cleared', 'success');
        } catch (error) {
            console.error('Clear cart error:', error);
            showNotification('Error', 'Failed to clear cart', 'error');
        }
    };

    return {
        api_base_url,
        cart,
        currentCategory,
        cartTotalPrice,
        totalCartItems,
        removeItem,
        updateItemQuantity,
        clearCart,
        loadCart,
        getIndexedDBData,
        saveIndexedDBData
    };
});