// src/stores/auth.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

// Function to get the CSRF token from cookies
const getCSRFToken = () => {
  const name = 'csrftoken';
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
};

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const loginError = ref('');

  // Login action
  const login = async (email, password) => {
    try {
      // Send login request and retrieve user data from response
      const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/login/`, {
        email,
        password,
      });

      user.value = response.data.user;  // Set user directly from response data
      console.log("User data:", user.value);
      console.log("Document cookie", document.cookie)

    } catch (error) {
      if (error.response && error.response.status === 401) {
        loginError.value = 'Incorrect email or password.';
      } else {
        loginError.value = 'An error occurred. Please try again later.';
      }
      throw error; // Re-throw the error for handling in the component
    }
  };

  // Logout action
  const logout = async () => {
    try {
      // Get CSRF token from cookies
      const csrfToken = getCSRFToken();

      // Send logout request to blacklist the token
      await axios.post(`${import.meta.env.VITE_API_BASE_URL}/logout/`, {}, {
        headers: {
          'X-CSRFToken': csrfToken, // Add CSRF token to the request headers
        },
      });

      user.value = null; // Clear user data upon successful logout
      console.log("Successfully logged out. User data cleared.");
    } catch (error) {
      console.error("Logout error:", error.response ? error.response.data : error);
      // Optionally handle errors here, e.g., show a notification
    }
  };

  return {
    user,
    loginError,
    login,
    logout, // Expose logout action
    isAuthenticated: computed(() => !!user.value),
  };
});
