import { defineStore } from 'pinia';
import axios from 'axios';
import { ref, watch } from 'vue';
import useNotifications from '@/store/notification';
import { debounce } from 'lodash'; // Added for debouncing

export const useEquipmentsStore = defineStore('equipmentStore', () => {
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  const { showNotification } = useNotifications();

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
  const filteredEquipments = ref([]);
  const nextPageUrl = ref(null);
  const previousPageUrl = ref(null);
  const totalPages = ref(1);
  const currentPage = ref(1);
  const totalItems = ref(0);
  const pageLinks = ref([]);
  const pageSize = ref(120);
  const relatedEquipments = ref([]);

  // Cache state
  const cache = ref({
    equipments: {},
    categories: null,
    relatedEquipments: {},
    selectedEquipment: {},
    timestamp: {},
  });

  // Track ongoing requests
  const pendingRequests = ref({});

  // Cache TTL (5 minutes)
  const CACHE_TTL = 5 * 60 * 1000;

  // Utility Functions
  const isCacheValid = (key) => {
    const timestamp = cache.value.timestamp[key];
    return timestamp && Date.now() - timestamp < CACHE_TTL;
  };

  const truncateText = (text, length) =>
    text.length > length ? `${text.slice(0, length)}...` : text;

  const deduplicateEquipments = (items) => {
    const seen = new Set();
    return items.filter((item) => {
      if (!item?.id) return false;
      if (seen.has(item.id)) return false;
      seen.add(item.id);
      return true;
    });
  };

  // Generic function to handle single requests
  const withSingleRequest = async (key, fn) => {
    // Return cached Promise if request is pending
    if (pendingRequests.value[key]) {
      return pendingRequests.value[key];
    }

    // Execute the request and store the Promise
    const promise = fn();
    pendingRequests.value[key] = promise;

    try {
      const result = await promise;
      return result;
    } finally {
      // Clear the pending request
      delete pendingRequests.value[key];
    }
  };

  // Actions
  const fetchRelatedEquipments = async (equipmentId) => {
    const cacheKey = `related_${equipmentId}`;
    if (cache.value.relatedEquipments[equipmentId] && isCacheValid(cacheKey)) {
      relatedEquipments.value = cache.value.relatedEquipments[equipmentId];
      return;
    }

    return withSingleRequest(`related_${equipmentId}`, async () => {
      isLoading.value = true;
      try {
        const response = await axios.get(`${api_base_url}/api/equipments/${equipmentId}/related/`);
        const data = deduplicateEquipments(response.data || []);
        relatedEquipments.value = data;
        cache.value.relatedEquipments[equipmentId] = data;
        cache.value.timestamp[cacheKey] = Date.now();
      } catch (error) {
        console.error('Error fetching related equipment:', error);
        showNotification('Error', 'Failed to fetch related equipments.', 'error');
      } finally {
        isLoading.value = false;
      }
    });
  };

  const fetchEquipments = async (url = `${api_base_url}/api/equipments/?page_size=${pageSize.value}`) => {
    const cacheKey = `equipments_${url}`;
    if (cache.value.equipments[url] && isCacheValid(cacheKey)) {
      const cached = cache.value.equipments[url];
      equipments.value = cached.data;
      nextPageUrl.value = cached.next;
      previousPageUrl.value = cached.previous;
      pageLinks.value = cached.page_links;
      totalPages.value = cached.total_pages;
      currentPage.value = cached.current_page;
      totalItems.value = cached.count;
      return;
    }

    return withSingleRequest(`equipments_${url}`, async () => {
      isLoading.value = true;
      error.value = null;

      try {
        const response = await axios.get(url, { withCredentials: true });
        const data = deduplicateEquipments(response.data?.results || []);

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

        equipments.value = data;
        nextPageUrl.value = enforceHttps(response.data?.next);
        previousPageUrl.value = enforceHttps(response.data?.previous);
        pageLinks.value = (response.data?.page_links || []).map((link) => ({
          ...link,
          url: enforceHttps(link.url),
        }));
        totalPages.value = response.data?.total_pages ?? 1;
        currentPage.value = response.data?.current_page ?? 1;
        totalItems.value = response.data?.count ?? 0;

        cache.value.equipments[url] = {
          data,
          next: nextPageUrl.value,
          previous: previousPageUrl.value,
          page_links: pageLinks.value,
          total_pages: totalPages.value,
          current_page: currentPage.value,
          count: totalItems.value,
        };
        cache.value.timestamp[cacheKey] = Date.now();
      } catch (err) {
        error.value = 'Failed to fetch equipments.';
        showNotification('Error', `Fetching equipments failed: ${err.response?.data || err.message}`, 'error');
      } finally {
        isLoading.value = false;
      }
    });
  };

  const fetchFilteredEquipments = async ({ category = '', search = '', categories = [], cities = [] } = {}) => {
    const cacheKey = JSON.stringify({ category, search, categories, cities });
    if (cache.value.equipments[cacheKey] && isCacheValid(`filtered_${cacheKey}`)) {
      equipments.value = cache.value.equipments[cacheKey].data;
      return;
    }

    return withSingleRequest(`filtered_${cacheKey}`, async () => {
      isLoading.value = true;
      error.value = null;

      try {
        const params = new URLSearchParams();
        if (category) params.append('category', category);
        if (search.trim()) params.append('search', search.trim());
        if (categories.length > 0) params.append('categories', categories.join(','));
        if (cities.length > 0) params.append('cities', cities.join(','));

        const url = `${api_base_url}/api/equipments/filter/?${params.toString()}`;
        const response = await axios.get(url, { withCredentials: true });
        const data = deduplicateEquipments(response.data?.results || []);

        equipments.value = data;
        cache.value.equipments[cacheKey] = { data };
        cache.value.timestamp[`filtered_${cacheKey}`] = Date.now();
      } catch (err) {
        showNotification('Error', `Fetching filtered equipments failed: ${err.response?.data || err.message}`, 'error');
      } finally {
        isLoading.value = false;
      }
    });
  };

  const fetchUserEquipments = async () => {
    const cacheKey = 'user_equipments';
    if (cache.value.equipments[cacheKey] && isCacheValid(cacheKey)) {
      userEquipments.value = cache.value.equipments[cacheKey].data;
      return;
    }

    return withSingleRequest(cacheKey, async () => {
      isLoading.value = true;
      error.value = null;

      try {
        const response = await axios.get(`${api_base_url}/api/user-equipment/`, { withCredentials: true });
        const data = deduplicateEquipments(response.data || []);
        userEquipments.value = data;
        cache.value.equipments[cacheKey] = { data };
        cache.value.timestamp[cacheKey] = Date.now();
      } catch (err) {
        error.value = 'Failed to fetch user equipments.';
        showNotification('Error', `Fetching user equipments failed: ${err.response?.data || err.message}`, 'error');
      } finally {
        isLoading.value = false;
      }
    });
  };

  const fetchUserEditableEquipments = async () => {
    const cacheKey = 'user_editable_equipments';
    if (cache.value.equipments[cacheKey] && isCacheValid(cacheKey)) {
      userEditableEquipmentsIds.value = cache.value.equipments[cacheKey].data;
      return;
    }

    return withSingleRequest(cacheKey, async () => {
      isLoading.value = true;
      error.value = null;

      try {
        const response = await axios.get(`${api_base_url}/api/user-editable-equipment/`, { withCredentials: true });
        const data = response.data || [];
        userEditableEquipmentsIds.value = data;
        cache.value.equipments[cacheKey] = { data };
        cache.value.timestamp[cacheKey] = Date.now();
      } catch (err) {
        error.value = 'Failed to fetch editable equipments.';
        showNotification('Error', `Fetching editable equipments failed: ${err.response?.data || err.message}`, 'error');
      } finally {
        isLoading.value = false;
      }
    });
  };

  const getEquipmentById = async (id) => {
    // if (!Number.isInteger(Number(id))) {
    //   error.value = 'Invalid equipment ID.';
    //   showNotification('Error', 'Invalid equipment ID.', 'error');
    //   return;
    // }

    const cacheKey = `equipment_${id}`;
    if (cache.value.selectedEquipment[id] && isCacheValid(cacheKey)) {
      selectedEquipment.value = cache.value.selectedEquipment[id];
      return;
    }

    const equipment = equipments.value.find((item) => item.id === Number(id));
    if (equipment) {
      selectedEquipment.value = equipment;
      cache.value.selectedEquipment[id] = equipment;
      cache.value.timestamp[cacheKey] = Date.now();
      return;
    }

    return withSingleRequest(cacheKey, async () => {
      isLoading.value = true;
      error.value = null;

      try {
        const response = await axios.get(`${api_base_url}/api/equipments/${id}/`, { withCredentials: true });
        selectedEquipment.value = response.data || null;
        if (response.data) {
          cache.value.selectedEquipment[id] = response.data;
          cache.value.timestamp[cacheKey] = Date.now();
        }
      } catch (err) {
        error.value = `Failed to fetch equipment with ID ${id}.`;
        showNotification('Error', `Fetching equipment failed: ${err.response?.data || err.message}`, 'error');
      } finally {
        isLoading.value = false;
      }
    });
  };

  const fetchCategories = async () => {
    const cacheKey = 'categories';
    if (categories.value.length > 0 || (cache.value.categories && isCacheValid(cacheKey))) {
      if (cache.value.categories) {
        categories.value = cache.value.categories;
      }
      return;
    }

    return withSingleRequest(cacheKey, async () => {
      isLoading.value = true;
      error.value = null;

      try {
        const response = await axios.get(`${api_base_url}/api/categories/`, { withCredentials: true });
        categories.value = response.data || [];
        cache.value.categories = response.data || [];
        cache.value.timestamp[cacheKey] = Date.now();
      } catch (err) {
        showNotification('Error', `Fetching categories failed: ${err.response?.data || err.message}`, 'error');
      } finally {
        isLoading.value = false;
      }
    });
  };

  // Pagination Actions
  const fetchNextPage = () => {
    if (nextPageUrl.value) {
      fetchEquipments(nextPageUrl.value);
    }
  };

  const fetchPreviousPage = () => {
    if (previousPageUrl.value) {
      fetchEquipments(previousPageUrl.value);
    }
  };

  const fetchPage = (pageUrl) => {
    if (pageUrl) {
      fetchEquipments(pageUrl);
    }
  };

  const setPageSize = (size) => {
    pageSize.value = size;
    fetchEquipments();
  };

  // Debounced watcher for filters
  const debouncedFetchFiltered = debounce(() => {
    fetchFilteredEquipments({
      search: searchQuery.value,
      categories: selectedCategories.value,
      cities: selectedCities.value,
    });
  }, 300);

  watch([searchQuery, selectedCategories, selectedCities], debouncedFetchFiltered, { deep: true });

  // Return state and actions
  return {
    totalPages,
    nextPageUrl,
    previousPageUrl,
    currentPage,
    totalItems,
    pageLinks,
    pageSize,
    truncateText,
    equipments,
    relatedEquipments,
    categories,
    selectedEquipment,
    userEquipments,
    userEditableEquipmentsIds,
    isLoading,
    error,
    searchQuery,
    selectedCategories,
    selectedCities,
    filteredEquipments,
    fetchEquipments,
    fetchRelatedEquipments,
    fetchFilteredEquipments,
    fetchUserEquipments,
    getEquipmentById,
    fetchUserEditableEquipments,
    fetchCategories,
    fetchNextPage,
    fetchPreviousPage,
    fetchPage,
    setPageSize,
  };
});