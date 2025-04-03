import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import useNotifications from '@/store/notification.js'; // Import the notification service

export const useCompanyInfoStore = defineStore('companyInfo', () => {
  // State variables
  const companyInfo = ref(null); // Holds the company information fetched from the API
  const loading = ref(false); // Flag to track if the data is being loaded
  const error = ref(null); // Error message (if any) when fetching the company info
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL; // API base URL from environment variables
  const { showNotification } = useNotifications();

  // Actions
  const fetchCompanyInfo = async () => {
    loading.value = true; // Set loading to true while fetching data
    error.value = null; // Reset any previous error

    try {
      // Make the API request to fetch company information
      const response = await axios.get(`${apiBaseUrl}/api/company-info/`);
      // Store the fetched company information in the state
      companyInfo.value = response.data;
    } catch (err) {
      // Handle error in case of failure
      error.value = err.response?.data?.detail || 'Failed to fetch company information.';
      showNotification('Error', `Failed to fetch company info: ${err.response?.data?.detail}`, 'error'); // Show error notification
    } finally {
      // Set loading to false after the request completes (whether successful or failed)
      loading.value = false;
    }
  };

  return {
    // Expose state variables and actions
    companyInfo,
    loading,
    error,
    fetchCompanyInfo,
  };
});
