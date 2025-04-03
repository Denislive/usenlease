import { setActivePinia, createPinia } from 'pinia';
import { useCartStore } from './cart';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';
import useNotifications from '@/store/notification.js';
import { useRoute } from 'vue-router';

// FILE: frontend/src/store/cart.test.js

jest.mock('axios');
jest.mock('@/store/auth');
jest.mock('@/store/notification.js');
jest.mock('vue-router');

describe('Cart Store', () => {
    let cartStore;
    let authStore;
    let showNotification;

    beforeEach(() => {
        setActivePinia(createPinia());
        cartStore = useCartStore();
        authStore = useAuthStore();
        showNotification = jest.fn();
        useNotifications.mockReturnValue({ showNotification });
        useRoute.mockReturnValue({ params: { cat: '' } });

        // Mock IndexedDB
        global.indexedDB = {
            open: jest.fn().mockReturnValue({
                onupgradeneeded: jest.fn(),
                onsuccess: jest.fn(),
                onerror: jest.fn(),
            }),
        };
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('loadCart - authenticated user', async () => {
        authStore.isAuthenticated = true;
        axios.get.mockResolvedValue({ data: [{ id: 1, name: 'Item 1' }] });

        await cartStore.loadCart();

        expect(axios.get).toHaveBeenCalledWith(`${cartStore.api_base_url}/api/cart-items/`, { withCredentials: true });
        expect(cartStore.cart).toEqual([{ id: 1, name: 'Item 1' }]);
    });

    test('loadCart - unauthenticated user', async () => {
        authStore.isAuthenticated = false;
        const mockData = [{ id: 1, name: 'Item 1' }];
        global.indexedDB.open.mockReturnValue({
            onsuccess: (event) => {
                event.target.result = {
                    transaction: jest.fn().mockReturnValue({
                        objectStore: jest.fn().mockReturnValue({
                            getAll: jest.fn().mockReturnValue({
                                onsuccess: (event) => {
                                    event.target.result = mockData;
                                },
                                onerror: jest.fn(),
                            }),
                        }),
                    }),
                };
            },
        });

        await cartStore.loadCart();

        expect(cartStore.cart).toEqual(mockData);
    });

    test('removeItem - item exists', async () => {
        cartStore.cart = [{ id: 1, name: 'Item 1' }];
        await cartStore.removeItem(1);

        expect(cartStore.cart).toEqual([]);
        expect(showNotification).not.toHaveBeenCalled();
    });

    test('removeItem - item does not exist', async () => {
        cartStore.cart = [{ id: 1, name: 'Item 1' }];
        await cartStore.removeItem(2);

        expect(cartStore.cart).toEqual([{ id: 1, name: 'Item 1' }]);
        expect(showNotification).toHaveBeenCalledWith('Error', 'Item not found in cart.', 'error');
    });

    test('updateItemQuantity - valid quantity', async () => {
        authStore.isAuthenticated = false;
        cartStore.cart = [{ id: 1, name: 'Item 1', quantity: 1, hourly_rate: 10, item: { available_quantity: 5 } }];
        await cartStore.updateItemQuantity(1, 3);

        expect(cartStore.cart[0].quantity).toBe(3);
        expect(cartStore.cart[0].total).toBe(30);
        expect(showNotification).toHaveBeenCalledWith('Quantity Updated', 'Item 1 quantity has been updated.', 'success');
    });

    test('updateItemQuantity - invalid quantity', async () => {
        cartStore.cart = [{ id: 1, name: 'Item 1', quantity: 1, hourly_rate: 10, item: { available_quantity: 5 } }];
        await cartStore.updateItemQuantity(1, -1);

        expect(cartStore.cart[0].quantity).toBe(1);
        expect(showNotification).toHaveBeenCalledWith('Invalid Quantity', 'Please enter a valid quantity.', 'error');
    });

    test('clearCart', async () => {
        cartStore.cart = [{ id: 1, name: 'Item 1' }];
        await cartStore.clearCart();

        expect(cartStore.cart).toEqual([]);
    });
});