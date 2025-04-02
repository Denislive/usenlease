<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100 p-4">
    <div class="w-full max-w-md bg-white rounded-xl shadow-lg overflow-hidden">
      <div class="p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-gray-800">Enter Verification Code</h2>
          <p class="mt-2 text-gray-600">
            We've sent a 6-digit code to {{ maskedEmail }}
          </p>
        </div>

        <!-- OTP Input -->
        <div class="mb-6">
          <label for="otp-input" class="sr-only">Enter OTP</label>
          <input
            id="otp-input"
            v-model="otp"
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            maxlength="6"
            autocomplete="one-time-code"
            placeholder="• • • • • •"
            class="w-full px-4 py-3 text-center text-xl font-medium tracking-widest border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
            @input="handleOtpInput"
            @paste.prevent="handleOtpPaste"
          />
        </div>

        <!-- Submit Button -->
        <button
          @click="submitOTP"
          :disabled="isSubmitting || otp.length !== 6"
          class="w-full py-3 px-4 bg-gray-900 text-white font-semibold rounded-lg hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="!isSubmitting">Verify</span>
          <span v-else class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Verifying...
          </span>
        </button>

        <!-- Resend OTP Section -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            Didn't receive the code?
            <button
              @click="requestNewOTP"
              :disabled="isTimerActive || isSubmitting"
              class="text-yellow-600 font-medium hover:text-yellow-700 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Resend OTP
            </button>
          </p>
          <p v-if="isTimerActive" class="mt-1 text-sm text-red-500">
            Please wait {{ remainingTime }} seconds before requesting a new code
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import useNotifications from '@/store/notification.js';
import Cookies from 'js-cookie';

const router = useRouter();
const { showNotification } = useNotifications();
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

// Reactive state
const otp = ref('');
const isSubmitting = ref(false);
const isTimerActive = ref(false);
const remainingTime = ref(60);
const email = ref(Cookies.get('email') || '');
let timerInterval = null;

// Computed properties
const maskedEmail = computed(() => {
  if (!email.value) return '';
  const [name, domain] = email.value.split('@');
  return `${name.substring(0, 3)}***@${domain}`;
});

// Input handlers
const handleOtpInput = (e) => {
  // Allow only numbers
  otp.value = e.target.value.replace(/\D/g, '');
  
  // Auto-submit when OTP is complete
  if (otp.value.length === 6) {
    submitOTP();
  }
};

const handleOtpPaste = (e) => {
  const pasteData = e.clipboardData.getData('text');
  const numbersOnly = pasteData.replace(/\D/g, '');
  otp.value = numbersOnly.substring(0, 6);
  
  if (otp.value.length === 6) {
    submitOTP();
  }
};

// Timer functions
const startTimer = () => {
  isTimerActive.value = true;
  remainingTime.value = 60;
  
  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    remainingTime.value -= 1;
    if (remainingTime.value <= 0) {
      clearInterval(timerInterval);
      isTimerActive.value = false;
    }
  }, 1000);
};

const clearTimer = () => {
  clearInterval(timerInterval);
  isTimerActive.value = false;
};

// API functions
const submitOTP = async () => {
  if (otp.value.length !== 6) {
    showNotification('Error', 'Please enter a 6-digit code', 'error');
    return;
  }

  isSubmitting.value = true;
  
  try {
    const response = await axios.post(
      `${apiBaseUrl}/api/accounts/otp/verify/`,
      { 
        otp: otp.value,
        email: email.value 
      },
      {
        timeout: 10000,
        withCredentials: true
      }
    );

    showNotification('Success', 'Account verified successfully', 'success');
    Cookies.remove('email');
    router.push('/login');
  } catch (error) {
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.detail || 
                        'Verification failed. Please try again.';
    showNotification('Error', errorMessage, 'error');
    
    // Clear OTP on error
    otp.value = '';
  } finally {
    isSubmitting.value = false;
  }
};

const requestNewOTP = async () => {
  if (!email.value) {
    showNotification('Error', 'Email not found. Please start the process again.', 'error');
    router.push('/register');
    return;
  }

  isSubmitting.value = true;
  
  try {
    await axios.post(
      `${apiBaseUrl}/api/accounts/otp/`,
      { email: email.value },
      {
        timeout: 10000,
        withCredentials: true
      }
    );
    
    showNotification('Success', 'New verification code sent', 'success');
    startTimer();
  } catch (error) {
    const errorMessage = error.response?.data?.message || 
                        'Failed to send new code. Please try again.';
    showNotification('Error', errorMessage, 'error');
  } finally {
    isSubmitting.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  if (!email.value) {
    showNotification('Error', 'Email not found. Please register again.', 'error');
    router.push('/register');
    return;
  }
  
  requestNewOTP();
});
</script>

<style scoped>
/* Custom transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>