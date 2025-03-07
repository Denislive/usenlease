<template>
  <div class="container mx-auto py-8">
    <!-- Cart Table -->
    <div v-if="cartItems.length > 0" class="overflow-x-auto mb-8">
      <table class="min-w-full bg-white border border-gray-300 rounded-lg shadow-md">
        <thead>
          <tr class="bg-gray-100 text-gray-600 uppercase text-sm leading-normal">
            <th class="py-3 px-6 text-left">Product</th>
            <th class="py-3 px-6 text-center">Quantity</th>
            <th class="py-3 px-6 text-right">Total</th>
          </tr>
        </thead>
        <tbody class="text-gray-600 text-sm font-light">
          <tr
            v-for="(item, index) in cartItems"
            :key="index"
            class="border-b border-gray-200 hover:bg-gray-100"
          >
            <td class="py-3 px-6">
              <img
                :src="`${getItemImage(item)}`"
                alt="Product Image"
                class="w-12 h-12 inline-block mr-4"
              />
              {{ getItemName(item) }}
            </td>
            <td class="py-3 px-6 text-center">
              {{ item.quantity }}
            </td>
            <td class="py-3 px-6 text-right">
              ${{ calculateItemTotal(item).toFixed(2) }}
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="bg-gray-100 font-semibold">
            <th class="py-3 px-6 text-left">Cart Subtotal</th>
            <td colspan="2" class="py-3 px-6 text-right">
              ${{ subtotal.toFixed(2) }}
            </td>
          </tr>
          <tr class="bg-gray-100 font-semibold">
            <th class="py-3 px-6 text-left">Service Fee (6%)</th>
            <td colspan="2" class="py-3 px-6 text-right">
              <strong>${{ serviceFee.toFixed(2) }}</strong>
            </td>
          </tr>
          <tr class="bg-gray-100 font-semibold">
            <th class="py-3 px-6 text-left">Shipping</th>
            <td colspan="2" class="py-3 px-6 text-right">
              <strong>${{ shippingCost.toFixed(2) }}</strong>
            </td>
          </tr>
          <tr class="bg-gray-100 border-t border-gray-300 font-bold">
            <th class="py-3 px-6 text-left">Order Total</th>
            <td colspan="2" class="py-3 px-6 text-right">
              <strong>${{ (subtotal + serviceFee + shippingCost).toFixed(2) }}</strong>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
    <!-- No Items Message -->
    <div v-else>
      <p class="text-gray-600 text-center py-8">Your cart is empty.</p>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref } from "vue";
import { useCartStore } from "@/store/cart";
import { useAuthStore } from "@/store/auth";
import useNotifications from '@/store/notification';

export default {
  setup() {
    const cartStore = useCartStore();
    const authStore = useAuthStore();
    const shippingCost = ref(0); // Fixed shipping cost

    const api_base_url = import.meta.env.VITE_API_BASE_URL;
    const { showNotification } = useNotifications();

    // Fetch the cart data
    const fetchCart = async () => {
      try {
        cartStore.loadCart(); // Load from Vuex or local storage
      } catch (error) {
        showNotification('Cart Error', `Failed to load cart data: ${ error.response?.data || error.message}!`, 'info');
      }
    };


    const calculateLeaseDuration = (item) => {
      const startDate = new Date(item.start_date);
      const endDate = new Date(item.end_date);
      const timeDiff = endDate - startDate;
      const days = timeDiff / (1000 * 3600 * 24); // Convert milliseconds to days
      return days;
    };

    // Calculate the total for a single item
    const calculateItemTotal = (item) => {
  const pricePerHour = authStore.isAuthenticated && item.item_details
    ? item.item_details.hourly_rate
    : item.item
    ? item.item.hourly_rate
    : 0;

  const rentalDays = calculateLeaseDuration(item) || 1; // Default to 1 day if not provided
  const totalHours = rentalDays; // Convert days to hours

  return pricePerHour * totalHours * item.quantity;
};


    // Calculate the subtotal
    const subtotal = computed(() => {
  return cartStore.cart.reduce((total, item) => {
    const pricePerHour = authStore.isAuthenticated && item.item_details
      ? item.item_details.hourly_rate
      : item.item
      ? item.item.hourly_rate
      : 0;

    const rentalDays = calculateLeaseDuration(item) || 1;
    const totalHours = rentalDays;

    return total + pricePerHour * totalHours * item.quantity;
  }, 0);
});


    // Calculate 6% service fee
    const serviceFee = computed(() => {
      return subtotal.value * 0.06; // 6% of subtotal
    });

    // Get item details dynamically based on authentication status
    const getItemImage = (item) => {
      return authStore.isAuthenticated && item.item_details
        ? item.item_details.images?.[0]?.image_url
        : item.item?.images?.[0]?.image_url || "/placeholder-image.jpg";
    };

    const getItemName = (item) => {
      return authStore.isAuthenticated && item.item_details
        ? item.item_details.name
        : item.item?.name || "Unknown Product";
    };

    // Load cart on component mount
    onMounted(() => {
      fetchCart();
    });

    return {
      api_base_url,
      cartItems: computed(() => cartStore.cart),
      subtotal,
      serviceFee,
      shippingCost,
      calculateItemTotal,
      getItemImage,
      getItemName,
    };
  },
};
</script>
