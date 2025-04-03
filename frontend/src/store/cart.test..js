import { setActivePinia, createPinia } from 'pinia';
import { useCartStore } from './cart';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';
import useNotifications from '@/store/notification.js';
import { useRoute } from 'vue-router';

// Mock all external dependencies
jest.mock('axios');
jest.mock('@/store/auth');
jest.mock('@/store/notification.js');
jest.mock('vue-router');

describe('Cart Store', () => {
    let cartStore;
    let authStore;
    let showNotification;
    let mockIndexedDB;

    // Sample test data
    const testCartItem = {
        id: 1,
        name: 'Test Item',
        quantity: 1,
        hourly_rate: 10,
        total: 10,
        item: { available_quantity: 5, name: 'Test Item' },
        item_details: { name: 'Test Item' }
    };

    beforeEach(() => {
        // Initialize Pinia and stores
        setActivePinia(createPinia());
        cartStore = useCartStore();
        authStore = useAuthStore();
        
        // Mock notification service
        showNotification = jest.fn();
        useNotifications.mockReturnValue({ showNotification });
        
        // Mock router
        useRoute.mockReturnValue({ params: { cat: '' } });

        // Enhanced IndexedDB mock
        mockIndexedDB = {
            _data: [],
            open: jest.fn().mockImplementation(() => ({
                onupgradeneeded: jest.fn(),
                onsuccess: jest.fn().mockImplementation(function(event) {
                    event.target.result = {
                        transaction: jest.fn().mockImplementation((storeName, mode) => ({
                            objectStore: jest.fn().mockReturnValue({
                                getAll: jest.fn().mockImplementation(() => ({
                                    onsuccess: jest.fn().mockImplementation(function(e) {
                                        e.target.result = [...mockIndexedDB._data];
                                    }),
                                    onerror: jest.fn()
                                })),
                                add: jest.fn().mockImplementation(item => {
                                    mockIndexedDB._data.push(item);
                                    return {
                                        onsuccess: jest.fn(),
                                        onerror: jest.fn()
                                    };
                                }),
                                clear: jest.fn().mockImplementation(() => {
                                    mockIndexedDB._data = [];
                                    return {
                                        onsuccess: jest.fn(),
                                        onerror: jest.fn()
                                    };
                                })
                            }),
                            oncomplete: jest.fn(),
                            onerror: jest.fn()
                        }))
                    };
                }),
                onerror: jest.fn()
            }))
        };

        global.indexedDB = mockIndexedDB;
        
        // Reset mock data
        mockIndexedDB._data = [];
        jest.clearAllMocks();
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    describe('loadCart', () => {
        test('should load cart for authenticated user', async () => {
            // Setup
            authStore.isAuthenticated = true;
            authStore.getCSRFToken = jest.fn().mockReturnValue('test-csrf-token');
            axios.get.mockResolvedValue({ 
                status: 200, 
                data: [testCartItem] 
            });

            // Execute
            await cartStore.loadCart();

            // Verify
            expect(axios.get).toHaveBeenCalledWith(
                `${cartStore.api_base_url}/api/cart-items/`, 
                {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': 'test-csrf-token'
                    }
                }
            );
            expect(cartStore.cart).toEqual([testCartItem]);
            expect(showNotification).not.toHaveBeenCalled();
        });

        test('should handle API error for authenticated user', async () => {
            // Setup
            authStore.isAuthenticated = true;
            axios.get.mockRejectedValue(new Error('Network error'));

            // Execute
            await cartStore.loadCart();

            // Verify
            expect(cartStore.cart).toEqual([]);
            expect(showNotification).toHaveBeenCalledWith(
                'Error', 
                'Could not load your cart items.', 
                'error'
            );
        });

        test('should load cart from IndexedDB for unauthenticated user', async () => {
            // Setup
            authStore.isAuthenticated = false;
            mockIndexedDB._data = [testCartItem];

            // Execute
            await cartStore.loadCart();

            // Verify
            expect(cartStore.cart).toEqual([testCartItem]);
            expect(axios.get).not.toHaveBeenCalled();
        });

        test('should handle IndexedDB error for unauthenticated user', async () => {
            // Setup
            authStore.isAuthenticated = false;
            mockIndexedDB.open.mockImplementation(() => ({
                onerror: jest.fn().mockImplementation(event => {
                    event.target.error = new Error('DB error');
                })
            }));

            // Execute
            await cartStore.loadCart();

            // Verify
            expect(cartStore.cart).toEqual([]);
        });
    });

    describe('removeItem', () => {
        test('should remove existing item for authenticated user', async () => {
            // Setup
            authStore.isAuthenticated = true;
            authStore.getCSRFToken = jest.fn().mockReturnValue('test-csrf-token');
            cartStore.cart = [testCartItem];
            axios.delete.mockResolvedValue({ status: 204 });

            // Execute
            await cartStore.removeItem(1);

            // Verify
            expect(axios.delete).toHaveBeenCalledWith(
                `${cartStore.api_base_url}/api/cart-items/1/`, 
                {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': 'test-csrf-token'
                    }
                }
            );
            expect(cartStore.cart).toEqual([]);
            expect(showNotification).toHaveBeenCalledWith(
                'Success', 
                'Item removed from cart', 
                'success'
            );
        });

        test('should remove existing item for unauthenticated user', async () => {
            // Setup
            authStore.isAuthenticated = false;
            cartStore.cart = [testCartItem];
            mockIndexedDB._data = [testCartItem];

            // Execute
            await cartStore.removeItem(1);

            // Verify
            expect(cartStore.cart).toEqual([]);
            expect(mockIndexedDB._data).toEqual([]);
            expect(axios.delete).not.toHaveBeenCalled();
        });

        test('should handle non-existent item', async () => {
            // Setup
            cartStore.cart = [testCartItem];

            // Execute
            await cartStore.removeItem(2);

            // Verify
            expect(cartStore.cart).toEqual([testCartItem]);
            expect(showNotification).toHaveBeenCalledWith(
                'Error', 
                'Failed to remove item from cart', 
                'error'
            );
        });
    });

    describe('updateItemQuantity', () => {
        test('should update quantity with valid input', async () => {
            // Setup
            authStore.isAuthenticated = false;
            cartStore.cart = [testCartItem];
            mockIndexedDB._data = [testCartItem];

            // Execute
            await cartStore.updateItemQuantity(1, 3);

            // Verify
            expect(cartStore.cart[0].quantity).toBe(3);
            expect(cartStore.cart[0].total).toBe(30);
            expect(mockIndexedDB._data[0].quantity).toBe(3);
            expect(showNotification).toHaveBeenCalledWith(
                'Success', 
                'Test Item quantity updated', 
                'success'
            );
        });

        test('should reject invalid quantity (negative)', async () => {
            // Setup
            cartStore.cart = [testCartItem];

            // Execute
            await cartStore.updateItemQuantity(1, -1);

            // Verify
            expect(cartStore.cart[0].quantity).toBe(1);
            expect(showNotification).toHaveBeenCalledWith(
                'Error', 
                'Please enter a valid quantity', 
                'error'
            );
        });

        test('should reject quantity exceeding availability', async () => {
            // Setup
            cartStore.cart = [testCartItem];

            // Execute
            await cartStore.updateItemQuantity(1, 10);

            // Verify
            expect(cartStore.cart[0].quantity).toBe(1);
            expect(showNotification).toHaveBeenCalledWith(
                'Error', 
                'Please enter a valid quantity', 
                'error'
            );
        });

        test('should handle API error for authenticated user', async () => {
            // Setup
            authStore.isAuthenticated = true;
            authStore.getCSRFToken = jest.fn().mockReturnValue('test-csrf-token');
            cartStore.cart = [testCartItem];
            axios.put.mockRejectedValue(new Error('Network error'));

            // Execute
            await cartStore.updateItemQuantity(1, 2);

            // Verify
            expect(showNotification).toHaveBeenCalledWith(
                'Error', 
                'Failed to update quantity', 
                'error'
            );
        });
    });

    describe('clearCart', () => {
        test('should clear cart for authenticated user', async () => {
            // Setup
            authStore.isAuthenticated = true;
            authStore.getCSRFToken = jest.fn().mockReturnValue('test-csrf-token');
            cartStore.cart = [testCartItem];
            axios.delete.mockResolvedValue({ status: 200 });

            // Execute
            await cartStore.clearCart();

            // Verify
            expect(axios.delete).toHaveBeenCalledWith(
                `${cartStore.api_base_url}/api/cart-items/clear/`, 
                {
                    withCredentials: true,
                    headers: {
                        'X-CSRFToken': 'test-csrf-token'
                    }
                }
            );
            expect(cartStore.cart).toEqual([]);
            expect(showNotification).toHaveBeenCalledWith(
                'Success', 
                'Cart cleared', 
                'success'
            );
        });

        test('should clear cart for unauthenticated user', async () => {
            // Setup
            authStore.isAuthenticated = false;
            cartStore.cart = [testCartItem];
            mockIndexedDB._data = [testCartItem];

            // Execute
            await cartStore.clearCart();

            // Verify
            expect(cartStore.cart).toEqual([]);
            expect(mockIndexedDB._data).toEqual([]);
            expect(axios.delete).not.toHaveBeenCalled();
        });

        test('should handle clear error', async () => {
            // Setup
            authStore.isAuthenticated = true;
            cartStore.cart = [testCartItem];
            axios.delete.mockRejectedValue(new Error('Network error'));

            // Execute
            await cartStore.clearCart();

            // Verify
            expect(showNotification).toHaveBeenCalledWith(
                'Error', 
                'Failed to clear cart', 
                'error'
            );
        });
    });

    describe('computed properties', () => {
        test('cartTotalPrice should calculate correct total', () => {
            // Setup
            cartStore.cart = [
                { ...testCartItem, total: 10 },
                { ...testCartItem, id: 2, total: 20 }
            ];

            // Verify
            expect(cartStore.cartTotalPrice).toBe(30);
        });

        test('totalCartItems should return correct count', () => {
            // Setup
            cartStore.cart = [testCartItem, { ...testCartItem, id: 2 }];

            // Verify
            expect(cartStore.totalCartItems).toBe(2);
        });

        test('currentCategory should return route param', () => {
            // Setup
            useRoute.mockReturnValue({ params: { cat: 'test-category' } });

            // Need to re-create store to get updated route mock
            const newCartStore = useCartStore();

            // Verify
            expect(newCartStore.currentCategory).toBe('test-category');
        });
    });
});