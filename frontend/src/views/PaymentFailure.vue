<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-lg max-w-sm w-full text-center">
      <!-- Payment failed icon -->
      <svg
        class="mx-auto h-24 w-24 text-red-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
      <h1 class="text-2xl font-semibold text-gray-800 mb-4">Payment Failed</h1>
      <p class="text-gray-600 mb-6">Your payment could not be completed. Please try again.</p>
      <button
        @click="retryPayment"
        class="bg-red-500 text-white py-2 px-4 rounded-lg hover:bg-red-600 transition duration-300"
      >
        Try Again
      </button>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    retryPayment() {
      this.$router.push('/checkout');
    },
  },
};
</script>
