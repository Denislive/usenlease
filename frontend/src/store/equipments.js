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

  // Fetch filtered equipments
  const fetchFilteredEquipments = async (query, category) => {
    try {
      const response = await axios.get(`${api_base_url}/api/equipments/search/`, {
        params: { q: query, category: category }
      });
      filteredEquipments.value = response.data; // Initial backend data
    } catch (error) {
      console.error('Error fetching filtered equipment:', error);
    }
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


// Fetch user equipments
const fetchUserEquipments = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/user-equipment/`, {
      withCredentials: true,  // This ensures cookies (credentials) are sent with the request
    });
    userEquipments.value = response.data;  // Assign the fetched equipment to `userEquipments`
  } catch (error) {
   
  }
};

// Fetch user editable equipments on mount with credentials
const fetchUserEditableEquipments = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/user-editable-equipment/`, {
      withCredentials: true,  // This ensures cookies (credentials) are sent with the request
    });
    userEditableEquipmentsIds.value = response.data;  // Assign the fetched equipment IDs
  } catch (error) {
    
  }
};


  // Get equipment by its ID
  const getEquipmentById = async (id) => {
    // Check if the equipment is already in the list to avoid unnecessary API calls
    const equipment = equipments.value.find((item) => item.id === id);
    if (equipment) {
      selectedEquipment.value = equipment; // Set selected equipment from the list
    } else {
      isLoading.value = true; // Set loading state to true
      error.value = null; // Reset any previous error
      try {
        // API request to fetch equipment details by ID
        const response = await axios.get(`${api_base_url}/api/equipments/${id}/`, {
          withCredentials: true, // Include credentials (cookies) in the request
        });
        selectedEquipment.value = response.data; // Store the fetched equipment
      } catch (err) {
        // Handle error if the request fails
        error.value = `Failed to fetch item with ID ${id}.`;
        showNotification('Item error', `Error fetching item by ID: ${err.response?.data || err.message}!`, 'error');

      } finally {
        // Set loading to false once the request is done (either success or failure)
        isLoading.value = false;
      }
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
    fetchFilteredEquipments,
    fetchUserEquipments,
    getEquipmentById,
    fetchUserEditableEquipments,
    fetchCategories,
    updateFilteredEquipments, // Manually trigger an update if needed
  };
});

