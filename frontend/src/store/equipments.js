import { defineStore } from 'pinia';
import { ref, computed, watch, reactive } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';
import useNotifications from '@/store/notification';
import { useRouter } from 'vue-router';

export const useEquipmentsStore = defineStore('equipmentStore', () => {
  // Dependencies
  const authStore = useAuthStore();
  const { showNotification } = useNotifications();
  const router = useRouter();

  // Configuration
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  if (!api_base_url) {
    console.error('API base URL is not configured');
    showNotification('Error', 'Application configuration error', 'error');
  }

  // State
  const equipments = ref([]);
  const categories = ref([]);
  const selectedEquipment = ref(null);
  const userEquipments = ref([]);
  const userEditableEquipmentsIds = ref([]);
  const selectedCategories = ref([]);
  const selectedCities = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const searchQuery = ref('');
  const lastFetchTimes = reactive({
    equipments: null,
    categories: null,
    userEquipments: null
  });
  const cacheDuration = 1000 * 60 * 5; // 5 minutes cache

  // Pagination state
  const pagination = reactive({
    nextPageUrl: null,
    previousPageUrl: null,
    totalPages: 1,
    currentPage: 1,
    totalItems: 0,
    pageLinks: [],
    pageSize: 12 // More reasonable default page size
  });

  const relatedEquipments = ref([]);

  // Getters
  const shouldFetchEquipments = computed(() => {
    return !lastFetchTimes.equipments || 
           Date.now() - lastFetchTimes.equipments > cacheDuration ||
           equipments.value.length === 0;
  });

  const shouldFetchCategories = computed(() => {
    return !lastFetchTimes.categories || 
           Date.now() - lastFetchTimes.categories > cacheDuration ||
           categories.value.length === 0;
  });

  const filteredEquipments = computed(() => {
    return equipments.value.filter(equipment => {
      const matchesSearch = searchQuery.value === '' || 
        equipment.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        equipment.description.toLowerCase().includes(searchQuery.value.toLowerCase());
      
      const matchesCategories = selectedCategories.value.length === 0 || 
        selectedCategories.value.includes(equipment.category);
      
      const matchesCities = selectedCities.value.length === 0 || 
        selectedCities.value.includes(equipment.city);
      
      return matchesSearch && matchesCategories && matchesCities;
    });
  });

  // Secure axios instance with interceptors
  const secureAxios = axios.create({
    baseURL: api_base_url,
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
  const fetchEquipments = async (url = `${api_base_url}/api/equipments/?page_size=${pagination.pageSize}`) => {
    if (!shouldFetchEquipments.value && url.includes('page_size')) {
      return; // Use cached data if still valid
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await secureAxios.get(url, {
        params: {
          t: Date.now() // Cache busting
        }
      });

      equipments.value = response.data?.results || [];
      
      // Update pagination state
      pagination.nextPageUrl = enforceHttps(response.data?.next);
      pagination.previousPageUrl = enforceHttps(response.data?.previous);
      pagination.pageLinks = (response.data?.page_links || []).map(link => ({
        ...link,
        url: enforceHttps(link.url)
      }));
      pagination.totalPages = response.data?.total_pages ?? 1;
      pagination.currentPage = response.data?.current_page ?? 1;
      pagination.totalItems = response.data?.count ?? 0;

      lastFetchTimes.equipments = Date.now();
    } catch (err) {
      handleError(err, 'Failed to fetch equipments');
    } finally {
      isLoading.value = false;
    }
  };

  const fetchRelatedEquipments = async (equipmentId) => {
    try {
      const response = await secureAxios.get(`/api/equipments/${equipmentId}/related/`);
      relatedEquipments.value = response.data;
    } catch (error) {
      handleError(error, 'Failed to fetch related equipment');
    }
  };

  const fetchFilteredEquipments = async (filters = {}) => {
    isLoading.value = true;
    error.value = null;

    try {
      const params = new URLSearchParams();

      if (filters.category) params.append('category', filters.category);
      if (filters.search?.trim()) params.append('search', filters.search.trim());
      if (filters.categories?.length > 0) params.append('categories', filters.categories.join(','));
      if (filters.cities?.length > 0) params.append('cities', filters.cities.join(','));

      const response = await secureAxios.get(`/api/equipments/filter/?${params.toString()}`);
      equipments.value = response.data?.results || [];
    } catch (err) {
      handleError(err, 'Failed to fetch filtered equipments');
    } finally {
      isLoading.value = false;
    }
  };

  const fetchUserEquipments = async () => {
    if (!authStore.isAuthenticated) return;

    try {
      const response = await secureAxios.get('/api/user-equipment/');
      userEquipments.value = response.data || [];
      lastFetchTimes.userEquipments = Date.now();
    } catch (err) {
      handleError(err, 'Failed to fetch user equipments');
    }
  };

  const fetchUserEditableEquipments = async () => {
    if (!authStore.isAuthenticated) return;

    try {
      const response = await secureAxios.get('/api/user-editable-equipment/');
      userEditableEquipmentsIds.value = response.data || [];
    } catch (err) {
      handleError(err, 'Failed to fetch editable equipments');
    }
  };

  const getEquipmentById = async (id) => {
    // Check local cache first
    const localEquipment = equipments.value.find(item => item.id === id) || 
                          userEquipments.value.find(item => item.id === id);
    
    if (localEquipment) {
      selectedEquipment.value = localEquipment;
      return;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await secureAxios.get(`/api/equipments/${id}/`);
      selectedEquipment.value = response.data || null;
    } catch (err) {
      handleError(err, `Failed to fetch equipment with ID ${id}`);
    } finally {
      isLoading.value = false;
    }
  };

  const fetchCategories = async () => {
    if (!shouldFetchCategories.value) return;

    isLoading.value = true;
    error.value = null;

    try {
      const response = await secureAxios.get('/api/categories/');
      categories.value = response.data || [];
      lastFetchTimes.categories = Date.now();
    } catch (err) {
      handleError(err, 'Failed to fetch categories');
    } finally {
      isLoading.value = false;
    }
  };

  // Helper functions
  const enforceHttps = (url) => {
    if (!url) return null;
    try {
      const urlObj = new URL(url);
      if (urlObj.protocol === 'http:') {
        urlObj.protocol = 'https:';
        return urlObj.toString();
      }
    } catch (e) {
      console.error('Invalid URL:', url);
    }
    return url;
  };

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

  // Watchers
  watch([searchQuery, selectedCategories, selectedCities], () => {
    fetchFilteredEquipments({ 
      search: searchQuery.value, 
      categories: selectedCategories.value, 
      cities: selectedCities.value 
    });
  }, { deep: true });

  return {
    // State
    equipments,
    categories,
    selectedEquipment,
    userEquipments,
    userEditableEquipmentsIds,
    isLoading,
    error,
    searchQuery,
    selectedCategories,
    selectedCities,
    relatedEquipments,
    filteredEquipments,
    ...toRefs(pagination),

    // Actions
    fetchEquipments,
    fetchRelatedEquipments,
    fetchFilteredEquipments,
    fetchUserEquipments,
    fetchUserEditableEquipments,
    getEquipmentById,
    fetchCategories,
    fetchNextPage: () => pagination.nextPageUrl && fetchEquipments(pagination.nextPageUrl),
    fetchPreviousPage: () => pagination.previousPageUrl && fetchEquipments(pagination.previousPageUrl),
    fetchPage: (pageUrl) => fetchEquipments(pageUrl),
    setPageSize: (size) => {
      pagination.pageSize = size;
      fetchEquipments();
    }
  };
});