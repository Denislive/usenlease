<template>
    <div>
      <h1>Payment Failed</h1>
      <p>Your payment could not be completed. Please try again.</p>
      <button @click="retryPayment">Try Again</button>
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
  