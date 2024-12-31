import { defineStore } from 'pinia';
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';
import CryptoJS from 'crypto-js'; // Import CryptoJS
import useNotifications from '@/store/notification';
import { useEquipmentsStore } from "@/store/equipments";

import { useCartStore } from './cart';
import { openDB, saveFormData, loadFormData, clearFormData } from '@/db/db'; // Import IndexedDB functions

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const apiEncryptKey = import.meta.env.VITE_ENCRYPTION_KEY;

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
  const store = useEquipmentsStore();

  const user = ref(null);
  const isOn = ref(false); // Initialize based on user's current role
  const redirectTo = ref('');
  const loginError = ref('');
  const isLoading = ref(false);
  const router = useRouter();
  const { showNotification } = useNotifications();
  const storedUser  = Cookies.get('user');

  const isAuthenticated = computed(() => !!user.value);

  // Decrypt stored user data if available
  onMounted(() => {
    if (storedUser ) {
      user.value = decryptData(storedUser ); // Decrypt the stored user data
      isOn.value = user.value?.role === 'lessor'; // Update isOn based on user role
      console.log('User  data decrypted and loaded:', user.value);
    }
  });

  const getUserData = async () => {
    try {
      const response = await axios.get(
        `${apiBaseUrl}/api/accounts/users/${user.value?.id}/`,
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
        console.log('User  data fetched and stored in cookies:', user.value);

        // Load any form data from IndexedDB
        const formDataArray = await loadFormData();
        console.log('Form data loaded from IndexedDB:', formDataArray);

        if (formDataArray.length > 0) {
          for (const data of formDataArray) {
            try {
              const createResponse = await axios.post(
                `${apiBaseUrl}/api/equipments/`,
                data,
                { withCredentials: true }
              );
              if (createResponse.status === 201) {
                showNotification(
                  'Item Listing Successful',
                  `${createResponse.data.name} created successfully!`,
                  'success'
                );
                console.log('Equipment created successfully:', createResponse.data);
              }
            } catch (error) {
              console.error('Error listing item from IndexedDB:', error);
            }
          }
        }
      } else {
        console.error(`Request completed but not successful. Status: ${response.status}`);
      }
    } catch (error) {
      console.error("Error fetching user data:", error);
    }
  };

  const updateUserRole = async () => {

    try {

      const updatedRole = user?.role === 'lessee' ? 'lessor' : 'lessee';

      const response = await axios.put(

        `${apiBaseUrl}/api/accounts/users/${user?.value.id}/`,

        { role: updatedRole },

        { withCredentials: true }

      );


      user.value.role = response.data.role;


      Cookies.set('user', encryptData(response.data), {

        sameSite: 'None',

        secure: true,

      });


      await getUserData();

      await store.fetchUserEquipments();

      router.push('/profile');


      showNotification('success', `You are now a ${updatedRole}.`, 'success');

    } catch (error) {

      console.error('Error updating role:', error);

      showNotification('error', 'Unable to switch role. Please try again.', 'error');

    }

  };


  const login = async (email, password, cart) => {
    isLoading.value = true;
    console.log('Attempting to log in with email:', email);
  
    try {
      const response = await axios.post(
        `${apiBaseUrl}/api/accounts/login/`,
        { email, password, cart },
        { withCredentials: true }
      );
  
      console.log('Login response received:', response);
  
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
          console.log('User  data cleared after timeout.');
        }, 86400000); // 24 hours in milliseconds
  
        showNotification('Login Successful', 'Welcome back!', 'success');
        console.log('User  logged in successfully:', user.value);
  
        // Load form data from IndexedDB and set owner
        const formDataArray = await loadFormData();
        console.log('Form data loaded from IndexedDB:', formDataArray);
  
        if (formDataArray.length > 0) {
          for (const data of formDataArray) {
            data.owner = user.value.id; // Set the owner to the logged-in user
            console.log('Preparing to create equipment with data:', data);
  
            // Convert base64 image to Blob if it exists
            if (data.images && data.images.base64) {
              const file = base64ToFile(data.images.base64, data.images.name); // Convert base64 to Blob
              const formData = new FormData();
              formData.append('image', file, data.images.name); // Append the file to FormData
  
              // Append other fields to FormData
              for (const key in data) {
                if (key !== 'images') { // Exclude the images field
                  formData.append(key, data[key]);
                }
              }
  
              try {
                const createResponse = await axios.post(
                  `${apiBaseUrl}/api/equipments/`,
                  formData,
                  { withCredentials: true, headers: { 'Content-Type': 'multipart/form-data' } }
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
                  console.log('Equipment created successfully:', createResponse.data);
                  await clearFormData();
                }
              } catch (error) {
                // Log the error response for debugging
                if (error.response) {
                  console.error('Error listing item from IndexedDB:', error);
                  console.error('Response data:', error.response.data);
                  console.error('Response status:', error.response.status);
                  showNotification(
                    'Error Listing Item',
                    `An error occurred during item listing: ${error.response.data.message || 'Unknown error'}`,
                    'error'
                  );
                } else {
                  console.error('Error without response:', error.message);
                  showNotification(
                    'Error Listing Item',
                    'An error occurred during item listing!',
                    'error'
                  );
                }
              }
            }
          }
        }
  
        const redirectPath = redirectTo.value || '/';
        redirectTo.value = '';
        router.push(redirectPath);
        loginError.value = '';
      } else {
        console.error("Login response not successful. Status:", response.status);
      }
    } catch (error) {
      // Improved error handling
      console.error('Error during login:', error); // Log the entire error object
      if (error.response) {
        // Server responded with a status other than 2xx
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
        console.error('Response headers:', error.response.headers);
        handleLoginError(error);
      } else if (error.request) {
        // Request was made but no response was received
        console.error('Request data:', error.request);
        loginError.value = 'No response from server. Please try again later.';
        showNotification('Login Error', 'No response from server. Please try again later.', 'error');
      } else {
        // Something happened in setting up the request
        console.error('Error message:', error.message);
        loginError.value = 'An error occurred. Please try again later.';
        showNotification('Login Error ', 'An error occurred. Please try again later.', 'error');
      }
    } finally {
      isLoading.value = false; // Reset loading state
    }
  };

  function base64ToFile(base64, filename) {
    // Split the base64 string into parts
    const arr = base64.split(',');
    const mime = arr[0].match(/:(.*?);/)[1]; // Extract the MIME type
    const bstr = atob(arr[1]); // Decode base64 string
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
  
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
  
    return new File([u8arr], filename, { type: mime }); // Create a File object
  }

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
        return true; // Indicate success
      } else {
        return false;
      }
    } catch (error) {
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
        console.error(`Logout response not successful. Status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error during logout:', error);
      showNotification('Logout Error', 'An error occurred while logging out.', 'error');
    } finally {
      isLoading.value = false; // Stop loading spinner
    }
  };

  const saveFormDataToIndexedDB = async (formData) => {
    try {
      await saveFormData(formData); // Save form data to IndexedDB
      console.log('Form data saved to IndexedDB:', formData);
    } catch (error) {
      console.error('Error saving form data to IndexedDB:', error);
    }
  };

  return {
    isOn,
    user,
    loginError,
    isLoading,
    login,
    logout,
    base64ToFile,
    getUserData,
    encryptData,
    refreshToken,
    redirectTo,
    isAuthenticated,
    updateUserRole,
    saveFormDataToIndexedDB, // Expose the function to save form data
  };
});