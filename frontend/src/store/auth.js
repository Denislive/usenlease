import { defineStore } from 'pinia';
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie'; // Import js-cookie for cookie management
import useNotifications from '@/store/notification'; // Import the notification service

// Function to get the CSRF token from cookies
const getCSRFToken = () => {
  const name = 'csrftoken';
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
};

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null); // Stores the user data
  const redirectTo = ref(''); // Path to redirect after login
  const loginError = ref('');
  const isLoading = ref(false);
  const router = useRouter(); // Router instance
  const { showNotification } = useNotifications(); // Initialize notification service

  // Check for user data in cookies on mount
  onMounted(() => {
    const storedUser = Cookies.get('user'); // Check for user cookie
    if (storedUser) {
      user.value = JSON.parse(storedUser); // Parse and set user data
      console.log("User data retrieved from cookies:", user.value); // Debug log
    }
  });


  

  // Login action
  const login = async (email, password) => {
    isLoading.value = true; // Set loading state
    console.log("Attempting to log in with email:", email);
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/accounts/login/`, {
        email,
        password,
      }, {
        withCredentials: true, // Important to send cookies with the request
      });

      user.value = response.data; // Set user data from response
      Cookies.set('user', JSON.stringify(user.value), { expires: 1 }); // Expires after 1 day

      // Schedule removal of user data after 1 day
      setTimeout(() => {
        logout(); // Automatically log out after 1 day
      }, 86400000); // 86400000 ms = 1 day

      console.log("Login successful! User data:", user.value); // Debug log for user data
      showNotification('Login Successful', 'Welcome back!', 'success'); // Show success notification

      // Attempt to load any pending form data from local storage
      const formData = loadFormDataFromLocalStorage();
      if (formData) {
        formData.set("owner", user.value.id); // Set the owner ID
        console.log("Equipment Payload: ", formData);
        console.log("User ID:", user.value.id);

        try {
          const createResponse = await axios.post("http://127.0.0.1:8000/api/equipments/", formData, {
            withCredentials: true // Important for sending HTTP-only cookies
          });
          console.log('Equipment created successfully:', createResponse.data);
          router.push({ name: 'equipment-details', params: { id: createResponse.data.id } }); // Redirect to the equipment details page
          showNotification('Item Listing Successful', `${createResponse.data.name} created successfully!`, 'success'); // Show success notification
          localStorage.removeItem('payload'); // Optionally remove the payload from local storage
          return;
        } catch (error) {
          console.error('Error creating equipment:', error.response.data);
          showNotification('Error Listing Item', "An error occured during item listing!", 'error'); // Show success notification

        }
      }

      // Redirect to intended route after login
      const redirectPath = redirectTo.value || '/'; // Get redirect path or default to '/'
      redirectTo.value = ''; // Reset redirect path
      router.push(redirectPath); // Redirect to intended route

      // Clear any previous errors
      loginError.value = '';
    } catch (error) {
      handleLoginError(error); // Handle login error
    } finally {
      isLoading.value = false; // Reset loading state
    }
  };

  const handleLoginError = (error) => {
    if (error.response && error.response.status === 401) {
      loginError.value = 'Incorrect email or password.';
      console.warn("Login failed: Incorrect email or password."); // Warn log for authentication failure
      showNotification('Login Failed', 'Incorrect email or password.', 'error'); // Show error notification
    } else {
      loginError.value = 'An error occurred. Please try again later.';
      console.error("Login error:", error); // Error log for other errors
      showNotification('Login Error', 'An error occurred. Please try again later.', 'error'); // Show error notification
    }
  };

  const logout = async () => {
    isLoading.value = true; // Set loading state
    console.log("Attempting to log out...");
    try {
      const csrfToken = getCSRFToken(); // Get CSRF token
      await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/accounts/logout/`, {}, {
        headers: {
          'X-CSRFToken': csrfToken, // Include CSRF token
        },
        withCredentials: true, // Ensure cookies are sent with the request
      });

      user.value = null; // Clear user data upon successful logout
      Cookies.remove('user'); // Remove user cookie
      console.log("Successfully logged out. User data cleared.");
      showNotification('Logout Successful', 'You have been logged out.', 'success'); // Show success notification
      router.push('/'); // Redirect to login after logout
    } catch (error) {
      console.error("Logout error:", error.response ? error.response.data : error);
      showNotification('Logout Error', 'An error occurred while logging out.', 'error'); // Show error notification
    } finally {
      isLoading.value = false; // Reset loading state
    }
  };

  // Check if the user is authenticated
  const isAuthenticated = computed(() => {
    const authenticated = !!user.value;
    console.log("Is user authenticated?", authenticated); // Debug log for authentication status
    return authenticated;
  });

  // Load form data from local storage
  const loadFormDataFromLocalStorage = () => {
    const payload = JSON.parse(localStorage.getItem('payload'));
    if (!payload) return null;

    const formData = new FormData();
    for (const key in payload) {
      if (payload[key].base64) {
        // Convert Base64 back to a File object
        const { base64, name, type } = payload[key];
        const file = base64ToFile(base64, name, type);
        formData.append(key, file);
      } else {
        formData.append(key, payload[key]);
      }
    }
    return formData;
  };

  // Helper function to convert Base64 string back to a File
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
    user,
    loginError,
    isLoading,
    login,
    logout,
    redirectTo, // Expose redirectTo
    isAuthenticated,
  };
});