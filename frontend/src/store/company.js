import { defineStore } from 'pinia';
import axios from 'axios';
import useNotifications from '@/store/notification.js'; // Import the notification service


export const useCompanyInfoStore = defineStore('companyInfo', {
  state: () => ({
    companyInfo: null, // Holds the company information fetched from the API
    loading: false, // Flag to track if the data is being loaded
    error: null, // Error message (if any) when fetching the company info
    api_base_url: import.meta.env.VITE_API_BASE_URL, // API base URL from environment variables
    showNotification: useNotifications() // Initialize notification service

  }),

  actions: {
    // Fetch company information from the API
    async fetchCompanyInfo() {
      this.loading = true; // Set loading to true while fetching data
      this.error = null; // Reset any previous error

      try {
        // Make the API request to fetch company information
        const response = await axios.get(`${this.api_base_url}/api/company-info/`);
        
        // Store the fetched company information in the state
        this.companyInfo = response.data;
      } catch (err) {
        // Handle error in case of failure
        this.error = err.response?.data?.detail || 'Failed to fetch company information.';
        this.showNotification('Error', `Error fetching company info: ${err}`, 'error'); // Show error notification

      } finally {
        // Set loading to false after the request completes (whether successful or failed)
        this.loading = false;
      }
    },
  },
});
