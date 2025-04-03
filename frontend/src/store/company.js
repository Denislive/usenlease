import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';
import useNotifications from '@/store/notification';
import { useRouter } from 'vue-router';

export const useCompanyInfoStore = defineStore('companyInfo', () => {
  // Dependencies
  const authStore = useAuthStore();
  const { showNotification } = useNotifications();
  const router = useRouter();

  // Configuration
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
  if (!apiBaseUrl) {
    console.error('API base URL is not configured');
    showNotification('Error', 'Application configuration error', 'error');
  }

  // State
  const companyInfo = ref(null);
  const loading = ref(false);
  const lastFetchTime = ref(null);
  const cacheDuration = 1000 * 60 * 5; // 5 minutes cache

  // Getters
  const companyData = computed(() => companyInfo.value?.data || null);
  const companyMetadata = computed(() => companyInfo.value?.meta || null);
  const shouldRefresh = computed(() => {
    if (!lastFetchTime.value) return true;
    return Date.now() - lastFetchTime.value > cacheDuration;
  });

  // Secure axios instance with interceptors
  const secureAxios = axios.create({
    baseURL: apiBaseUrl,
    withCredentials: true
  });

  secureAxios.interceptors.request.use(config => {
    if (authStore.isAuthenticated && authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  }, error => {
    return Promise.reject(error);
  });

  secureAxios.interceptors.response.use(response => {
    return response;
  }, error => {
    if (error.response?.status === 401) {
      authStore.logout();
      router.push('/login');
    }
    return Promise.reject(error);
  });

  // Actions
  const fetchCompanyInfo = async (forceRefresh = false) => {
    if (!forceRefresh && !shouldRefresh.value && companyInfo.value) {
      return; // Use cached data if still valid
    }

    loading.value = true;
    try {
      const response = await secureAxios.get('/api/company-info/', {
        params: {
          t: Date.now() // Cache busting
        }
      });

      companyInfo.value = response.data;
      lastFetchTime.value = Date.now();
    } catch (error) {
      handleError(error, 'Failed to fetch company information');
      throw error; // Re-throw for components to handle if needed
    } finally {
      loading.value = false;
    }
  };

  const updateCompanyInfo = async (updateData) => {
    if (!companyInfo.value) {
      await fetchCompanyInfo();
    }

    loading.value = true;
    try {
      const response = await secureAxios.patch('/api/company-info/', updateData, {
        headers: {
          'Content-Type': 'application/merge-patch+json'
        }
      });

      companyInfo.value = response.data;
      showNotification('Success', 'Company information updated successfully', 'success');
      return response.data;
    } catch (error) {
      handleError(error, 'Failed to update company information');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // Helper functions
  const handleError = (error, defaultMessage) => {
    const message = error.response?.data?.detail || 
                    error.response?.data?.message || 
                    defaultMessage;
    
    // Don't show notification for 401 errors (handled by interceptor)
    if (error.response?.status !== 401) {
      showNotification('Error', message, 'error');
    }
    
    console.error(error);
  };

  const resetCompanyInfo = () => {
    companyInfo.value = null;
    lastFetchTime.value = null;
  };

  return {
    // State
    loading,
    
    // Getters
    companyData,
    companyMetadata,
    
    // Actions
    fetchCompanyInfo,
    updateCompanyInfo,
    resetCompanyInfo
  };
});