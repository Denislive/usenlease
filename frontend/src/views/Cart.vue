<template>
  <div class="container md:py-1 lg:py-1 mx-auto sm:p-0">
    <!-- Shopping Cart Area Start -->
    <div class="mt-0">
      <form @submit.prevent="submitCart">
        <h3 class="bg-gray-800 text-white p-4 mb-4">Cart Summary</h3>
        <div class="overflow-x-auto p-2">
          <table class="min-w-full bg-white border border-gray-300">
            <thead>
              <tr>
                <th class="py-2 px-4 border-b text-left">Delete</th>
                <th class="py-2 px-4 border-b text-left">Image</th>
                <th class="py-2 px-4 border-b text-left">Product</th>
                <th class="py-2 px-4 border-b text-left">Price</th>
                <th class="py-2 px-4 border-b text-left">Quantity</th>
                <th class="py-2 px-4 border-b text-left">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in cartItems" :key="item.id">
                <td class="py-2 px-4 border-b">
                  <button @click.prevent="removeFromCart(item)">
                    <i class="pi pi-trash text-red-500"></i>
                  </button>
                </td>
                <td class="py-2 px-4 border-b">
                  <img :src="`http://127.0.0.1:8000${item.images[0].image_url}`" alt="" class="w-20 h-20 object-cover" />
                </td>
                <td class="py-2 px-4 border-b">
                  <a href="#" class="text-blue-600 hover:underline">{{ item.name }}</a>
                </td>
                <td class="py-2 px-4 border-b">${{ item.hourly_rate.toFixed(2) }}</td>
                <td class="py-2 px-4 border-b">
                  <div class="border-b">
                    <button @click.prevent="adjustQuantity(item, -1)" class="text-red-500 m-0" :disabled="item.quantity <= 1">
                      <i class="pi pi-minus lg:mr-4"></i>
                    </button>
                    <span class="mx-2 text-xl">{{ item.quantity }}</span>
                    <button @click.prevent="adjustQuantity(item, 1)" class="text-yellow-500">
                      <i class="pi pi-plus lg:ml-4"></i>
                    </button>
                  </div>
                </td>
                <td class="py-2 px-4 border-b">${{ item.total.toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Cart Totals Area Start -->
        <div class="mt-8">
          <h3 class="font-semibold bg-gray-800 text-white p-4 mb-4">Cart Totals</h3>
          <div class="m-4">
            <div class="flex justify-between">
              <p>Subtotal</p>
              <p class="font-semibold">${{ subtotal.toFixed(2) }}</p>
            </div>
            <div class="flex justify-between">
              <p>Shipping</p>
              <p class="font-semibold">Flat Rate: $25.00</p>
            </div>
            <div class="flex justify-between mt-2">
              <p>Total</p>
              <p class="font-semibold">${{ (subtotal + 25).toFixed(2) }}</p>
            </div>
          </div>
          <div class="text-right m-4">
            <button @click.prevent="checkout" class="bg-[#1c1c1c] text-white py-2 px-4 rounded hover:text-[#ffc107] transition">Proceed to Checkout</button>
          </div>
        </div>
        <!-- Cart Totals Area End -->
      </form>
    </div>
    <!-- Shopping Cart Area End -->
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useCartStore } from '@/store/cart'; // Adjust the path as necessary

export default {
  setup() {
    const cartStore = useCartStore();

    // Load the cart from local storage when the component mounts
    cartStore.loadCart();


    const submitCart = () => {
      console.log('Cart submitted:', cartStore.cart);
      // Here you can add the logic to handle the submitted cart
    };

    const removeFromCart = (item) => {
      cartStore.removeItem(item.id);
    };

    const adjustQuantity = (item, adjustment) => {
      const newQuantity = item.quantity + adjustment;
      if (newQuantity >= 0) {
        cartStore.updateItemQuantity(item.id, newQuantity);
      }
    };
    

    const checkout = () => {
      console.log('Proceeding to checkout');
      // Handle checkout process
    };

    return {
      cartItems: cartStore.cart, // Reference cart from store
      subtotal: computed(() => cartStore.cartTotalPrice), // Computed property for total price from store
      submitCart,
      removeFromCart,
      adjustQuantity,
      checkout,
    };
  },
};
</script>

<style scoped>
/* Add any additional styles here */
</style>
