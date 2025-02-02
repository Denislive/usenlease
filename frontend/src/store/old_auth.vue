import { defineStore } from 'pinia';
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';
import CryptoJS from 'crypto-js'; // Import CryptoJS
import useNotifications from '@/store/notification';
import { useCartStore } from './cart';


const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const apiEncryptKey = import.meta.env.VITE_ENCRYPTION_KEY;

const encryptData = (data) => {
  return CryptoJS.AES.encrypt(JSON.stringify(data), apiEncryptKey).toString();
};

const decryptData = (data) => {
  const bytes = CryptoJS.AES.decrypt(data, apiEncryptKey);
  return JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
};

export const useAuthStore = defineStore('auth', () => {
  const cartStore = useCartStore();

  const user = ref(null);
  const isOn = ref(user?.role === 'lessor'); // Initialize based on user's current role
  const redirectTo = ref('');
  const loginError = ref('');
  const isLoading = ref(false);
  const router = useRouter();
  const { showNotification } = useNotifications();

  const storedUser  = Cookies.get('user');

  const isAuthenticated = computed(() => !!user.value);



  onMounted(() => {
    if (storedUser ) {
      user.value = decryptData(storedUser ); // Decrypt the stored user data
    }
  });


const getUserData = async () => {
  try {
    const response = await axios.get(
      `${apiBaseUrl}/api/accounts/users/${user?.id}/`,
      { withCredentials: true }
    );
    
    if (response.status === 200) {
      user.value = {
        ...response.data,
        user_address: response.data.user_address || {
          full_name: '',
          street_address: '',
          street_address2: '',
          city: '',
          state: '',
          zip_code: '',
          country: ''
        }
      };
      // Encrypt the user data and store it in cookies
      Cookies.set('user', encryptData(user.value), {
        sameSite: 'None',
        secure: true,

      });

    } else {
      console.error(`Request completed but not successful.`);
    }
  } catch (error) {
    console.error("Error fetching user data:");
    // Handle error
  }
};

const login = async (email, password, cart) => {
  isLoading.value = true;

  try {
    const response = await axios.post(
      `${apiBaseUrl}/api/accounts/login/`,
      { email, password, cart },
      { withCredentials: true }
    );

    if (response.status === 200) {

      user.value = response.data;

      // Encrypt user data and store in a secure cookie
      Cookies.set('user', encryptData(user.value), {
        sameSite: 'None',
        secure: true,
      });

      // Automatically remove the cookie after 24 hours
      setTimeout(() => {
        Cookies.remove('user');
        user.value = null; // Clear user data
      }, 86400000); // 24 hours in milliseconds

      showNotification('Login Successful', 'Welcome back!', 'success');

      // Handle form data for equipment listing
      const formData = loadFormDataFromLocalStorage();
      if (formData) {
        formData.set('owner', user.value.id);

        try {
          const createResponse = await axios.post(
            `${apiBaseUrl}/api/equipments/`,
            formData,
            { withCredentials: true }
          );

          if (createResponse.status === 201) {
            router.push({
              name: 'equipment-details',
              params: { id: createResponse.data.id },
            });
            showNotification(
              'Item Listing Successful',
              `${createResponse.data.name} created successfully!`,
              'success'
            );

            // Clear saved form data
            localStorage.removeItem('payload');
          } else {
            showNotification(
              'Error Listing Item',
              'Failed to list the item. Please try again later.',
              'error'
            );
          }
        } catch (error) {
          console.error('Error listing item:', error);
          showNotification(
            'Error Listing Item',
            'An error occurred while listing the item.',
            'error'
          );
        }
      }

      // Redirect to the intended page or default to home
      const redirectPath = redirectTo.value || '/';
      redirectTo.value = '';
      router.push(redirectPath);

      loginError.value = '';
    } else {
      showNotification('Login Failed', 'Unexpected response from server.', 'error');
    }
  } catch (error) {
    console.error('Error occurred during login or equipment listing:', error);
  
    // Check if the error has a response (for API errors)
    if (error.response) {
      console.error('Response error:', error.response);
      showNotification(
        'Login Failed',
        `Error: ${error.response.status} - ${error.response.statusText}`,
        'error'
      );
    } else if (error.request) {
      // Handle errors with the request
      console.error('Request error:', error.request);
      showNotification(
        'Login Failed',
        'No response received from server. Please check your connection.',
        'error'
      );
    } else {

      // Handle other types of errors (e.g., setup errors)
      console.error('General error:', error.message);
      showNotification(
        'Login Failed',
        'An unexpected error occurred. Please try again later.',
        'error'
      );
    }
  }finally {
    isLoading.value = false;
  }
};

  const refreshToken = async () => {
    try {
      const response = await axios.post(
        `${apiBaseUrl}/api/accounts/token/refresh/`,
        {}, // No payload needed, as cookies are used
        { withCredentials: true } // Ensure cookies are sent with the request
      );
  
      if (response.status === 200) {
        console.log("Token refreshed successfully.");
        return true; // Indicate success
      } else {
        console.error("Failed to refresh token.");
        return false;
      }
    } catch (error) {
      console.error("Error refreshing token:", error);
      return false;
    }
  };


  axios.interceptors.response.use(
    (response) => response, // Pass through successful responses
    async (error) => {
      const originalRequest = error.config;
  
      if (error.response && error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true; // Prevent infinite retry loop
  
        // Attempt to refresh the token
        const tokenRefreshed = await refreshToken();
  
        if (tokenRefreshed) {
          // Retry the original request with the refreshed token
          return axios(originalRequest);
        } else {
          // Redirect to login if refresh fails
          console.warn("Redirecting to login due to token refresh failure.");
          router.push('/login'); // Ensure router is properly imported and accessible
          return Promise.reject(error);
        }
      }
  
      return Promise.reject(error);
    }
  );
  
  

  const logout = async () => {
    isLoading.value = true;
    try {
  
      const response = await axios.post(
        `${apiBaseUrl}/api/accounts/logout/`,
        {},
        {
          withCredentials: true,
        }
      );
  
      if (response.status === 200) {
  
        // Clear user data
        user.value = null; // Reactive state for the user
        Cookies.remove('user'); // Remove user cookie
  
        // Clear cart data
        cartStore.clearCart();
  
        // Notify user of success
        showNotification('Logout Successful', 'You have been logged out.', 'success');
  
        // Redirect to home page
        router.push('/');
      } else {
        console.error(`Logout response not successful.`);
      }
    } catch (error) {
      console.error('Error during logout:');
      showNotification('Logout Error', 'An error occurred while logging out.', 'error');
    } finally {
      isLoading.value = false; // Stop loading spinner
    }
  };
  
  
 
  const loadFormDataFromLocalStorage = () => {
    const payload = JSON.parse(localStorage.getItem('payload'));
    if (!payload) return null;

    const formData = new FormData();
    Object.entries(payload).forEach(([key, value]) => {
      if (value.base64) {
        const { base64, name, type } = value;
        const file = base64ToFile(base64, name, type);
        formData.append(key, file);
      } else {
        formData.append(key, value);
      }
    });
    return formData;
  };

  const base64ToFile = (base64, fileName, mimeType) => {
    const byteString = atob(base64.split(',')[1]);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new File([ab], fileName, { type: mimeType });
  };

  return {
    isOn,
    user,
    loginError,
    isLoading,
    login,
    logout,
    getUserData,
    encryptData,
    refreshToken,
    redirectTo,
    isAuthenticated,
  };
});