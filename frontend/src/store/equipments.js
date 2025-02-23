import { defineStore } from 'pinia';
import axios from 'axios';
import { ref, watch } from 'vue';
import useNotifications from '@/store/notification';

export const useEquipmentsStore = defineStore('equipments', () => {
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  const { showNotification } = useNotifications();

  // State variables
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

  // ✅ Use `ref([])` instead of `computed` for filtered equipments
  const filteredEquipments = ref([]);

  // Truncate text utility function
  const truncateText = (text, length) => {
    return text.length > length ? text.slice(0, length) + '...' : text;
  };

  // Fetch Equipments
  const fetchEquipments = async () => {
    if (equipments.value.length > 0) return;
    isLoading.value = true;
    error.value = null;

    try {
      const response = await axios.get(`${api_base_url}/api/equipments/`, {
        withCredentials: true,
      });

      equipments.value = response.data;
      updateFilteredEquipments(); // Ensure filtering runs after fetching
    } catch (err) {
      error.value = 'Failed to fetch items.';
      showNotification('Items error', `Error fetching items: ${err.response?.data || err.message}!`, 'error');
    } finally {
      isLoading.value = false;
    }
  };

  // Fetch Categories
  const fetchCategories = async () => {
    if (categories.value.length > 0) return;
    isLoading.value = true;
    error.value = null;

    try {
      const response = await axios.get(`${api_base_url}/api/categories/`, {
        withCredentials: true,
      });

      categories.value = response.data;
    } catch (err) {
      error.value = 'Failed to fetch categories.';
      showNotification('Items error', `Error fetching categories: ${err.response?.data || err.message}!`, 'error');
    } finally {
      isLoading.value = false;
    }
  };

  // ✅ Function to manually update `filteredEquipments`
  const updateFilteredEquipments = () => {
    const query = searchQuery.value.trim().toLowerCase();

    filteredEquipments.value = equipments.value.filter((equipment) => {
      const matchesQuery =
        query === '' ||
        equipment.name.toLowerCase().includes(query) ||
        equipment.description?.toLowerCase().includes(query) ||
        equipment.hourly_rate.toString().includes(query) ||
        equipment.address?.street_address?.toLowerCase().includes(query) ||
        equipment.address?.city?.toLowerCase().includes(query) ||
        equipment.address?.state?.toLowerCase().includes(query);

      // Get active filters
      const activeCategories = Object.keys(selectedCategories.value).filter((key) => selectedCategories.value[key]);
      const activeCities = Object.keys(selectedCities.value).filter((key) => selectedCities.value[key]);

      // ✅ Ensure category filtering works correctly
      const matchesCategory =
        activeCategories.length === 0 || (equipment.category && activeCategories.includes(equipment.category));

      const matchesCity =
        activeCities.length === 0 || (equipment.address?.city && activeCities.includes(equipment.address.city));

      return matchesQuery && matchesCategory && matchesCity;
    });

    console.log("🔍 Updated Filtered Equipments:", filteredEquipments.value.length);
  };

  // ✅ Watchers to keep `filteredEquipments` reactive
  watch([equipments, searchQuery, selectedCategories, selectedCities], updateFilteredEquipments, { deep: true });

  return {
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
    filteredEquipments, // ✅ Now a ref([]), not computed!
    fetchEquipments,
    fetchCategories,
    updateFilteredEquipments, // Manually trigger an update if needed
  };
});
