<template>
    <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center py-12">
      <div class="max-w-4xl w-full bg-white shadow-md rounded-lg p-8">
        <div class="text-center mb-6">
          <h1 class="text-3xl font-bold text-green-600">Payment Successful!</h1>
          <p v-if="orderId" class="text-lg text-gray-700 mt-2">Your payment was processed successfully. Thank you for your purchase!</p>
          <p v-else class="text-lg text-gray-700 mt-2">Loading payment details...</p>
        </div>
  
        <div v-if="orderDetails" class="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Order Summary</h2>
          <div class="mb-2">
            <p><span class="font-medium text-gray-700">Order ID:</span> {{ orderDetails.order_id }}</p>
            <p><span class="font-medium text-gray-700">Payment Status:</span> <span class="text-green-600 font-bold">{{ orderDetails.payment_status }}</span></p>
            <p><span class="font-medium text-gray-700">Total Items in the order:</span> {{ orderDetails.total_order_items }}</p>
            <p><span class="font-medium text-gray-700">Total Amount Deducted:</span> ${{ orderDetails.order_total_price }}</p>
          </div>
  
          <p class="text-gray-700 mt-4">You can follow your order in your <a href="/profile" class="text-blue-600 font-medium hover:underline">profile</a>. A confirmation email has also been sent to you.</p>
        </div>
  
        <p v-if="error" class="text-red-600 font-bold mt-6">{{ error }}</p>
  
        <div class="mt-8 text-center">
          <a href="/" class="text-[#1c1c1c] font-medium hover:underline">Back to Home</a>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  const api_base_url = import.meta.env.VITE_API_BASE_URL;

  
  export default {
    data() {
      return {
        orderId: null,
        orderDetails: null,
        error: null,
      };
    },
    mounted() {
      // Extract the session ID and order ID from the query parameters
      const session_id = this.$route.query.session_id;
  
      if (!session_id) {
        this.error = "Session ID not provided.";
        return;
      }
  
      // Call backend API to retrieve the session details
      axios
        .get(`${api_base_url}/api/session-status/`, {
          params: { session_id: session_id },
        })
        .then((response) => {
          if (response.data.session_status === "complete") {
            this.orderDetails = response.data;
            this.orderId = response.data.order_id;
          } else {
            this.error = "Payment not yet confirmed.";
          }
        })
        .catch((error) => {
          this.error = error.response?.data?.error || "Failed to retrieve payment details.";
        });
    },
  };
  </script>
  
  <style scoped>
  .min-h-screen {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: #f7fafc;
  }
  </style>
  