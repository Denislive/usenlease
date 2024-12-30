import { defineStore } from 'pinia';
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';
import CryptoJS from 'crypto-js'; // Import CryptoJS
import useNotifications from '@/store/notification';
import { useCartStore } from './cart';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const apiEncryptKey = import.meta.env.VITE_ENCRYPTION_KEY

const encryptData = (data) => {
  return CryptoJS.AES.encrypt(JSON.stringify(data), apiEncryptKey).toString();
};

const decryptData = (data) => {
  try {
    const bytes = CryptoJS.AES.decrypt(data, apiEncryptKey);
    const decryptedData = bytes.toString(CryptoJS.enc.Utf8);
    return decryptedData ? JSON.parse(decryptedData) : null;
  } catch (error) {
    console.error('Error decrypting data:', error);
    return null; // Return null if decryption fails
  }
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

  // Decrypt stored user data if available
  onMounted(() => {
    if (storedUser) {
      user.value = decryptData(storedUser); // Decrypt the stored user data
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

        // Encrypt user data before storing in cookies
        Cookies.set('user', encryptData(response.data), {
          sameSite: 'None',
          secure: true,
        });

        // Set a timeout for 24 hours to remove the cookie
        setTimeout(() => {
          Cookies.remove('user');
          user.value = null; // Clear user data
        }, 86400000); // 24 hours in milliseconds

        showNotification('Login Successful', 'Welcome back!', 'success');

        // Check if storedUser exists before attempting decryption
        if (storedUser) {
          user.value = decryptData(storedUser);
        }

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
              localStorage.removeItem('payload');
            } else {
              console.error("Item listing response not successful. Status:");
            }
          } catch (error) {
            showNotification(
              'Error Listing Item',
              'An error occurred during item listing!',
              'error'
            );
          }
        }

        const redirectPath = redirectTo.value || '/';
        redirectTo.value = '';
        router.push(redirectPath);
        loginError.value = '';
      } else {
        console.error("Login response not successful.");
      }
    } catch (error) {
      console.error(`Error during login. ${error}`);
      handleLoginError(error);
    } finally {
      isLoading.value = false;
    }
  };

  const handleLoginError = (error) => {
    if (error.response?.status === 401) {
      loginError.value = 'Incorrect email or password.';
      showNotification('Login Failed', 'Incorrect email or password.', 'error');
    } else {
      loginError.value = 'An error occurred. Please try again later.';
      showNotification(
        'Login Error',
        'An error occurred. Please try again later.',
        'error'
      );
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
        { withCredentials: true }
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
