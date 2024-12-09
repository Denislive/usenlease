<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100">
    <div class="flex flex-col items-center p-8 bg-white rounded-lg shadow-lg w-80">
      <h2 class="text-2xl font-semibold mb-6 text-[#1c1c1c]">Enter OTP</h2>
      <input type="text" v-model="otp" maxlength="6" placeholder="Enter OTP"
        class="border border-gray-300 text-gray-700 text-center font-medium p-3 rounded w-full mb-6 focus:outline-none focus:ring-2 focus:ring-[#ffc107] placeholder-gray-400"
        @input="autoSubmit" />
      <button @click="submitOTP" :disabled="isSubmitting"
        class="bg-[#1c1c1c] text-white font-semibold p-3 rounded w-full mb-4 hover:bg-yellow-500 disabled:opacity-50">
        Submit
      </button>
      <div v-if="isTimerActive" class="text-red-500 mb-4 text-sm">
        Resend OTP in: {{ remainingTime }} seconds
      </div>
      <button v-if="!isTimerActive" @click="requestNewOTP" :disabled="isSubmitting"
        class="border border-[#ffc107] text-[#ffc107] font-semibold p-3 rounded w-full hover:bg-[#ffc107] hover:text-white disabled:opacity-50">
        Request New OTP
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import useNotifications from '@/store/notification.js';
import Cookies from 'js-cookie';

export default {
  setup() {
    const otp = ref('');
    const router = useRouter();
    const { showNotification } = useNotifications();

    const isSubmitting = ref(false);
    const isTimerActive = ref(false);
    const remainingTime = ref(60);
    const email = ref(Cookies.get('email'));
    let timerInterval;

    const autoSubmit = () => {
      if (otp.value.length === 6) {
        submitOTP();
      }
    };


    // Example function to delete the email cookie
    function deleteEmailCookie() {
      Cookies.remove('email');
    }

    const submitOTP = async () => {
      if (!otp.value) {
        showNotification("Error", "Please enter the OTP.", "error");
        return;
      }
      isSubmitting.value = true;
      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/api/accounts/otp/verify/`,
          { otp: otp.value, email: email.value },

        );
        showNotification("Success", "OTP verified successfully.", "success");
        router.push('/login');
        // Usage example
        deleteEmailCookie();
      } catch (error) {
        showNotification("Error", error.response?.data || "OTP verification failed.", "error");
      } finally {
        isSubmitting.value = false;
      }
    };

    const requestNewOTP = async () => {
      isSubmitting.value = true;
      try {
        await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/api/accounts/otp/`,
          { email: email.value },
        );
        showNotification("Success", "New OTP sent to your email.", "success");
        startTimer();
      } catch (error) {
        showNotification("Error", error.response?.data || "Failed to send new OTP.", "error");
      } finally {
        isSubmitting.value = false;
      }
    };

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
      requestNewOTP();

    });

    return {
      otp,
      isSubmitting,
      isTimerActive,
      remainingTime,
      submitOTP,
      requestNewOTP,
      autoSubmit,
    };
  },
};

</script>

<style>
/* Add any additional global styles here */
</style>
