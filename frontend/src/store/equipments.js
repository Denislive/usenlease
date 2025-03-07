import { defineStore } from 'pinia';
import axios from 'axios';
import { ref, watch } from 'vue';
import useNotifications from '@/store/notification';
import { toArray } from 'lodash';

export const useEquipmentsStore = defineStore('equipmentStore', () => {
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  const { showNotification } = useNotifications();

  const equipments = ref([]);
  const categories = ref([]);
  const selectedEquipment = ref(null);
  const userEquipments = ref([]);
  const userEditableEquipmentsIds = ref([]);
  const selectedCategories = ref({});
  const selectedCities = ref({});
  const isLoading = ref(false);
  const error = ref(null);
  const searchQuery = ref('');

  const filteredEquipments = ref([]);

  const truncateText = (text, length) => 
    text.length > length ? text.slice(0, length) + '...' : text;

  // Pagination variables
  const nextPageUrl = ref(null);
  const previousPageUrl = ref(null);
  const totalPages = ref(1);
  const currentPage = ref(1);
  const totalItems = ref(0);
  const pageLinks = ref([]);
  const pageSize = ref(120);

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

      updateFilteredEquipments();
    } catch (err) {
      error.value = 'Failed to fetch equipments.';
      showNotification('Error', `Fetching equipments failed: ${err.response?.data || err.message}`, 'error');
    } finally {
      isLoading.value = false;
    }
  };

  const fetchNextPage = () => nextPageUrl.value && fetchEquipments(nextPageUrl.value);
  const fetchPreviousPage = () => previousPageUrl.value && fetchEquipments(previousPageUrl.value);
  const fetchPage = (pageUrl) => pageUrl && fetchEquipments(pageUrl);
  const setPageSize = (size) => {
    pageSize.value = size;
    fetchEquipments();
  };

  const fetchUserEquipments = async () => {
    try {
      const response = await axios.get(`${api_base_url}/api/user-equipment/`, { withCredentials: true });
      userEquipments.value = response.data || [];
    } catch (err) {
      showNotification('Error', `Fetching user equipments failed: ${err.response?.data || err.message}`, 'error');
    }
  };

  const fetchUserEditableEquipments = async () => {
    try {
      const response = await axios.get(`${api_base_url}/api/user-editable-equipment/`, { withCredentials: true });
      userEditableEquipmentsIds.value = response.data || [];
    } catch (err) {
      showNotification('Error', `Fetching editable equipments failed: ${err.response?.data || err.message}`, 'error');
    }
  };

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

  const fetchCategories = async () => {
    if (categories.value.length > 0) return;

    isLoading.value = true;
    error.value = null;

    try {
      const response = await axios.get(`${api_base_url}/api/categories/`, { withCredentials: true });
      categories.value = response.data || [];
    } catch (err) {
      error.value = 'Failed to fetch categories.';
      showNotification('Error', `Fetching categories failed: ${err.response?.data || err.message}`, 'error');
    } finally {
      isLoading.value = false;
    }
  };

  const updateFilteredEquipments = () => {
    if (!equipments.value.length) {
      filteredEquipments.value = [];
      return;
    }

    const query = searchQuery.value.trim().toLowerCase();

    filteredEquipments.value = equipments.value.filter((equipment) => {
      const matchesQuery =
        !query ||
        equipment.name?.toLowerCase().includes(query) ||
        equipment.description?.toLowerCase().includes(query) ||
        equipment.hourly_rate?.toString().includes(query) ||
        equipment.address?.street_address?.toLowerCase().includes(query) ||
        equipment.address?.city?.toLowerCase().includes(query) ||
        equipment.address?.state?.toLowerCase().includes(query);

      const activeCategories = Object.keys(selectedCategories.value).filter((key) => selectedCategories.value[key]);
      const activeCities = Object.keys(selectedCities.value).filter((key) => selectedCities.value[key]);

      const matchesCategory =
        activeCategories.length === 0 || (equipment.category && activeCategories.includes(equipment.category));

      const matchesCity =
        activeCities.length === 0 || (equipment.address?.city && activeCities.includes(equipment.address.city));

      return matchesQuery && matchesCategory && matchesCity;
    });
  };

  watch([equipments, searchQuery, selectedCategories, selectedCities], updateFilteredEquipments, { deep: true });

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
    fetchUserEquipments,
    getEquipmentById,
    fetchUserEditableEquipments,
    fetchCategories,
    updateFilteredEquipments,
    fetchNextPage,
    fetchPreviousPage,
    fetchPage,
    setPageSize,
  };
});
