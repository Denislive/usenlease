import { defineStore } from 'pinia';
import axios from 'axios';
import { ref, watch } from 'vue';
import useNotifications from '@/store/notification';

export const useEquipmentsStore = defineStore('equipmentStore', () => {
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  const { showNotification } = useNotifications();

  // State
  const equipments = ref([]);
  const categories = ref([]);
  const selectedEquipment = ref(null);
  const userEquipments = ref([]);
  const userEditableEquipmentsIds = ref([]);
  const selectedCategories = ref([]); // Changed to array for multiple selections
  const selectedCities = ref([]); // Changed to array for multiple selections
  const isLoading = ref(false);
  const error = ref(null);
  const searchQuery = ref('');
  const filteredEquipments = ref([]);

  // Pagination state
  const nextPageUrl = ref(null);
  const previousPageUrl = ref(null);
  const totalPages = ref(1);
  const currentPage = ref(1);
  const totalItems = ref(0);
  const pageLinks = ref([]);
  const pageSize = ref(120);

  // Utility function
  const truncateText = (text, length) =>
    text.length > length ? `${text.slice(0, length)}...` : text;

  // Actions

  /**
   * Fetch all equipments with pagination support.
   * @param {string} url - The URL to fetch equipments from (defaults to the first page).
   */
  const fetchEquipments = async (url = `${api_base_url}/api/equipments/?page_size=${pageSize.value}`) => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await axios.get(url, { withCredentials: true });

      equipments.value = response.data?.results || [];
      nextPageUrl.value = response.data?.next || null;
      previousPageUrl.value = response.data?.previous || null;
      totalPages.value = response.data?.total_pages ?? 1;
      currentPage.value = response.data?.current_page ?? 1;
      totalItems.value = response.data?.count ?? 0;
      pageLinks.value = response.data?.page_links || [];
    } catch (err) {
      error.value = 'Failed to fetch equipments.';
      showNotification('Error', `Fetching equipments failed: ${err.response?.data || err.message}`, 'error');
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Fetch filtered equipments based on category, search query, selected categories, and cities.
   * @param {Object} filters - An object containing filter parameters.
   * @param {string} filters.category - The category to filter by.
   * @param {string} filters.search - The search query.
   * @param {string[]} filters.categories - An array of selected categories.
   * @param {string[]} filters.cities - An array of selected cities.
   */
  const fetchFilteredEquipments = async ({ category = '', search = '', categories = [], cities = [] } = {}) => {
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

      equipments.value = response.data?.results || [];
    } catch (err) {
      showNotification('Error', `Fetching filtered equipments failed: ${err.response?.data || err.message}`, 'error');
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Fetch the next page of equipments.
   */
  const fetchNextPage = () => {
    if (nextPageUrl.value) {
      fetchEquipments(nextPageUrl.value);
    }
  };

  /**
   * Fetch the previous page of equipments.
   */
  const fetchPreviousPage = () => {
    if (previousPageUrl.value) {
      fetchEquipments(previousPageUrl.value);
    }
  };

  /**
   * Fetch a specific page of equipments.
   * @param {string} pageUrl - The URL of the page to fetch.
   */
  const fetchPage = (pageUrl) => {
    if (pageUrl) {
      fetchEquipments(pageUrl);
    }
  };

  /**
   * Set the page size and refetch equipments.
   * @param {number} size - The new page size.
   */
  const setPageSize = (size) => {
    pageSize.value = size;
    fetchEquipments();
  };

  /**
   * Fetch equipments associated with the current user.
   */
  const fetchUserEquipments = async () => {
    try {
      const response = await axios.get(`${api_base_url}/api/user-equipment/`, { withCredentials: true });
      userEquipments.value = response.data || [];
    } catch (err) {
      showNotification('Error', `Fetching user equipments failed: ${err.response?.data || err.message}`, 'error');
    }
  };

  /**
   * Fetch equipments that the current user can edit.
   */
  const fetchUserEditableEquipments = async () => {
    try {
      const response = await axios.get(`${api_base_url}/api/user-editable-equipment/`, { withCredentials: true });
      userEditableEquipmentsIds.value = response.data || [];
    } catch (err) {
      showNotification('Error', `Fetching editable equipments failed: ${err.response?.data || err.message}`, 'error');
    }
  };

  /**
   * Fetch a specific equipment by its ID.
   * @param {number} id - The ID of the equipment to fetch.
   */
  const getEquipmentById = async (id) => {
    const equipment = equipments.value.find((item) => item.id === id);
    if (equipment) {
      selectedEquipment.value = equipment;
      return;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await axios.get(`${api_base_url}/api/equipments/${id}/`, { withCredentials: true });
      selectedEquipment.value = response.data || null;
    } catch (err) {
      error.value = `Failed to fetch equipment with ID ${id}.`;
      showNotification('Error', `Fetching equipment failed: ${err.response?.data || err.message}`, 'error');
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Fetch all categories.
   */
  const fetchCategories = async () => {
    if (categories.value.length > 0) {
      return;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await axios.get(`${api_base_url}/api/categories/`, { withCredentials: true });
      categories.value = response.data || [];
    } catch (err) {
      showNotification('Error', `Fetching categories failed: ${err.response?.data || err.message}`, 'error');
    } finally {
      isLoading.value = false;
    }
  };

  // Watch for changes in searchQuery, selectedCategories, and selectedCities
  watch([searchQuery, selectedCategories, selectedCities], () => {
    fetchFilteredEquipments({ search: searchQuery.value, categories: selectedCategories.value, cities: selectedCities.value });
  }, { deep: true });

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