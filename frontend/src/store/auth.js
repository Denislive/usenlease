import { defineStore } from 'pinia';
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';
import CryptoJS from 'crypto-js'; // Import CryptoJS
import useNotifications from '@/store/notification';
import { useEquipmentsStore } from "@/store/equipments";

import { useCartStore } from './cart';
import Profile from '@/components/Profile.vue';
import autoprefixer from 'autoprefixer';

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

function getCSRFToken() {
  const csrfCookie = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
  return csrfCookie ? csrfCookie.split('=')[1] : null;
}

axios.defaults.headers.common['X-CSRFToken'] = getCSRFToken();

export const useAuthStore = defineStore('auth', () => {
  const cartStore = useCartStore();
  const store = useEquipmentsStore();

  const redirectTo = ref('');

  const user = ref(null);
  const isOn = ref(user?.role === 'lessor'); // Initialize based on user's current role

  const showSidebar = ref(true); // Sidebar visibility state


  const loginError = ref('');
  const isLoading = ref(false);
  const router = useRouter();
  const { showNotification } = useNotifications();
  const storedUser  = Cookies.get('user');

  const activeSection = ref('personal-info');

    // Computed property for active section based on user role

    const roleSection = computed(() => {

      return user?.value.role !== 'lessor' ? 'my-orders' : 'my-equipments';

    });

  const isAuthenticated = computed(() => !!user.value);

  // Decrypt stored user data if available
  onMounted(() => {
    if (storedUser ) {
      user.value = decryptData(storedUser ); // Decrypt the stored user data
      isOn.value = user.value?.role === 'lessor'; // Update isOn based on user role
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
              
      } else {
        console.error(`Request completed but not successful. Status: ${response.status}`);
      }
    } catch (error) {
      console.error("Error fetching user data:", error);
    }
  };

    // Function to navigate to a section
    const navigateToRoleSection = (sectionName) => {

      console.log("navigating to role", sectionName);
      console.log("role section value", roleSection.value);
      
      activeSection.value = roleSection.value;
      
      
      // Scroll to the section
      const sectionElement = document.getElementById(sectionName);
      if (sectionElement) {
        sectionElement.scrollIntoView({ behavior: "smooth" });
      }

      // Hide sidebar on small devices
      if (window.innerWidth < 1024) {
        showSidebar.value = false;
      }

    };


    const updateUserRole = async () => {
      try {
        // Proceed with updating the role first
        const updatedRole = user?.value.role === 'lessee' ? 'lessor' : 'lessee';
        showNotification('Role Update Pending', `Updating your role to ${updatedRole}. Please wait...`, 'info');
    
        // Wait for the role update to complete
        const response = await axios.put(
          `${apiBaseUrl}/api/accounts/users/${user?.value.id}/`,
          { role: updatedRole },
          { withCredentials: true }
        );
    
        // After the role is updated, update the local user object and store in cookies
        user.value.role = response.data.role;
        Cookies.set('user', encryptData(response.data), {
          sameSite: 'None',
          secure: true,
        });
    
        // Fetch updated user data and navigate
        await getUserData();

        if (user?.value.role === 'lessee') {
          router.push('/new-profile/orders');
        } else if (user?.value.role === 'lessor') {
          router.push('/new-profile/items');
        } else {
          router.push('/new-profile');
        }        

        navigateToRoleSection(roleSection.value);
    
        // Fetch user equipment data after the role change
        await store.fetchUserEquipments();
    
        showNotification('Role Update Successful', `You are now a ${updatedRole}.`, 'success');
    
    
      } catch (error) {
        console.error('Error updating role:', error);
        showNotification('Error', 'Unable to switch role. Please try again.', 'error');
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
  
        Cookies.set('user', encryptData(response.data), {
          sameSite: 'None',
          secure: true,
        });
  
        setTimeout(() => {
          Cookies.remove('user');
          user.value = null;
        }, 86400000);
  
        showNotification('Login Successful', 'Welcome back!', 'success');

        loginError.value = '';
      } else {
        console.error('Login response not successful. Status:', response.status);
      }
    } catch (error) {
      handleLoginError(error);
    } finally {
           
      isLoading.value = false;
    }
  };
  

  const handleCreateError = (error) => {
    if (error.response) {
      // Server responded with an error
      const errorMessage = error.response.data.error || error.response.data.detail || 'Unknown error';
      showNotification('Info', errorMessage, 'info');
    } else if (error.request) {
      // Request was made but no response was received
      showNotification('Network Error', 'No response from server. Please check your connection.', 'error');
    } else {
      // Something else happened in setting up the request
      showNotification('Error', `Error: ${error.message}`, 'error');
    }
  };
  

  const handleLoginError = (error) => {
    let errorMessage = 'An error occurred. Please try again later.';
    let notificationType = 'error'; // Default notification type
  
    if (error.response) {
      // Extract error message from different possible fields
      errorMessage = error.response.data?.details || 
                     error.response.data?.error || 
                     error.response.data?.message || 
                     errorMessage;
  
      switch (error.response.status) {
        case 400:
          errorMessage = errorMessage || 'Invalid request. Please check your input.';
          break;
        case 401:
          errorMessage = errorMessage || 'Incorrect email or password.';
          break;
        case 403:
          errorMessage = errorMessage || 'Account not verified. Please check your email.';
          notificationType = 'info'; // Change notification type to info
          break;
        case 429:
          errorMessage = errorMessage || 'Too many login attempts. Try again later.';
          break;
        case 500:
          errorMessage = errorMessage || 'Server error. Please try again later.';
          break;
        case 503:
          errorMessage = errorMessage || 'Service temporarily unavailable. Try again later.';
          break;
      }
    } else if (error.request) {
      // No response received (e.g., network issues)
      errorMessage = 'Network issue. Please check your connection.';
    } else {
      // Something else happened
      errorMessage = error.message || errorMessage;
    }
  
    // Update UI
    loginError.value = errorMessage;
    showNotification(`Login ${notificationType}`, errorMessage, notificationType, 0);
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
          // Clear user data
          user.value = null; // Reactive state for the user
          Cookies.remove('user'); // Remove user cookie
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
      // Clear user data
      user.value = null; // Reactive state for the user
      Cookies.remove('user'); // Remove user cookie

      if (response.status === 200) {
        // Clear user data
        user.value = null; // Reactive state for the user
        Cookies.remove('user'); // Remove user cookie
        // Notify user of success
        showNotification('Logout Successful', 'You have been logged out.', 'success', 0);
        // Redirect to home page
        router.push('/');

        // Clear cart data
        cartStore.clearCart();
      } else {
      }
    } catch (error) {
    } finally {
      isLoading.value = false; // Stop loading spinner
    }
  };

 
 

  return {
    isOn,
    user,
    redirectTo,
    loginError,
    isLoading,
    getCSRFToken,
    activeSection,
    showSidebar,
    login,
    logout,
    getUserData,
    encryptData,
    decryptData,
    refreshToken,
    isAuthenticated,
    updateUserRole,
    navigateToRoleSection,
  };
});