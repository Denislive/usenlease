<template>
  <div class="flex flex-col items-center p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-xl font-semibold mb-4">Enter OTP</h2>
    <input
      type="text"
      v-model="otp"
      maxlength="6"
      placeholder="Enter OTP"
      class="border border-gray-300 p-2 rounded w-64 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400"
    />
    <button
      @click="submitOTP"
      :disabled="isSubmitting || isTimerActive"
      class="bg-blue-500 text-white p-2 rounded w-full mb-2 hover:bg-blue-600 disabled:opacity-50"
    >
      Submit
    </button>
    <div v-if="isTimerActive" class="text-red-600 mb-2">
      Resend OTP in: {{ remainingTime }} seconds
    </div>
    <button
      v-if="!isTimerActive"
      @click="requestNewOTP"
      :disabled="isSubmitting"
      class="bg-green-500 text-white p-2 rounded w-full hover:bg-green-600 disabled:opacity-50"
    >
      Request New OTP
    </button>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const otp = ref('');
    const isSubmitting = ref(false);
    const isTimerActive = ref(false);
    const remainingTime = ref(60);
    const email = ref(localStorage.getItem('email')); // Retrieve email from local storage
    let timerInterval;

    // Function to submit the OTP
    const submitOTP = async () => {
      if (!otp.value) {
        alert("Please enter the OTP.");
        return;
      }

      isSubmitting.value = true;
      try {
        const response = await axios.post(
          'http://127.0.0.1:8000/api/accounts/otp/verify/',
          { otp: otp.value, email: email.value }, // Include email in the request
          { withCredentials: true }
        );
        console.log('OTP verified:', response.data);

        // Optionally remove the email from local storage after verification
        localStorage.removeItem('email');

        // Handle success (e.g., redirect the user or show a success message)
      } catch (error) {
        console.error('Error verifying OTP:', error.response?.data || error);
      } finally {
        isSubmitting.value = false;
      }
    };

    // Function to request a new OTP
    const requestNewOTP = async () => {
      isSubmitting.value = true;

      try {
        await axios.post(
          'http://127.0.0.1:8000/api/accounts/otp/',
          { email: email.value }, // Include email in the request
          { withCredentials: true }
        );
        console.log('New OTP requested for email:', email.value);
        startTimer(); // Start the countdown timer
      } catch (error) {
        console.error('Error requesting new OTP:', error.response?.data || error);
      } finally {
        isSubmitting.value = false;
      }
    };

    // Function to start the timer
    const startTimer = () => {
      isTimerActive.value = true;
      remainingTime.value = 60;

      timerInterval = setInterval(() => {
        remainingTime.value -= 1;
        if (remainingTime.value <= 0) {
          clearInterval(timerInterval);
          isTimerActive.value = false;
        }
      }, 1000);
    };

    onMounted(() => {
      if (!email.value) {
        console.error('No email found in local storage.');
      }
    });

    return {
      otp,
      isSubmitting,
      isTimerActive,
      remainingTime,
      submitOTP,
      requestNewOTP,
    };
  },
};
</script>

<style>
/* Add any additional global styles here */
</style>

