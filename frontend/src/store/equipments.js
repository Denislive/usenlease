import { defineStore } from 'pinia';
import axios from 'axios';
import { ref } from 'vue';
import useNotifications from '@/store/notification';


export const useEquipmentsStore = defineStore('equipments', () => {
  // API base URL from environment variables
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  const { showNotification } = useNotifications();


  // State variables
  const equipments = ref([]);
  const categories = ref([]);
  const selectedEquipment = ref(null);
  const isLoading = ref(false);
  const error = ref(null);
  const userEquipments = ref([]);
  const userEditableEquipmentsIds = ref([]);

  const totalBooked = ref(0);
  const bookedDates = ref(null);

  const truncateText = (text, length) => {
    if (text.length > length) {
      return text.slice(0, length) + '...';
    }
    return text;
  };

// Fetch user equipments
const fetchUserEquipments = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/user-equipment/`, {
      withCredentials: true,  // This ensures cookies (credentials) are sent with the request
    });
    userEquipments.value = response.data;  // Assign the fetched equipment to `equipments`
  } catch (error) {
    // Check if the error has a response (for API errors)
    if (error.response) {
     
    } else if (error.request) {
      // Handle errors with the request (no response received)
      console.error('Request error:', error.request);
      showNotification(
        'Error Fetching Equipments',
        'No response received from server. Please check your connection.',
        'error'
      );
    } else {
      // Handle other types of errors (e.g., setup errors)
      console.error('General error:', error.message);
      showNotification(
        'Error Fetching Equipments',
        'An unexpected error occurred. Please try again later.',
        'error'
      );
    }
  }
};

// Fetch user equipments on mount with credentials
const fetchUserEditableEquipments = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/user-editable-equipment/`, {
      withCredentials: true,  // This ensures cookies (credentials) are sent with the request
    });
    userEditableEquipmentsIds.value = response.data;  // Assign the fetched equipment to `equipments`
    console.log(userEditableEquipmentsIds.value);
    
  } catch (error) {
    // Check if the error has a response (for API errors)
    if (error.response) {
     
    } else if (error.request) {
      // Handle errors with the request (no response received)
      console.error('Request error:', error.request);
      showNotification(
        'Error Fetching Equipments',
        'No response received from server. Please check your connection.',
        'error'
      );
    } else {
      // Handle other types of errors (e.g., setup errors)
      console.error('General error:', error.message);
      showNotification(
        'Error Fetching Equipments',
        'An unexpected error occurred. Please try again later.',
        'error'
      );
    }
  }
};

const fetchEquipments = async () => {
  if (equipments.value.length > 0) return; // Avoid refetching if already loaded
  isLoading.value = true; // Set loading state to true
  error.value = null; // Reset any previous error

  try {
    // API request to fetch equipments with booked dates and total booked
    const response = await axios.get(`${api_base_url}/api/equipments/`, {
      withCredentials: true,  // Ensure credentials are sent with the request
    });

    // Log the raw response data for inspection
    console.log('Raw response data:', response.data);

    // Process the data and map it to include totalBooked and bookedDates
    equipments.value = response.data.map((equipment) => {
      const mappedEquipment = {
        ...equipment,
      };
      
      // Log each equipment object after mapping
      console.log('Mapped equipment:', mappedEquipment);
      
      return mappedEquipment;
    });

  } catch (err) {
    error.value = 'Failed to fetch items.'; 
    showNotification('Items error', `Error fetching items: ${err.response?.data || err.message}!`, 'error');
    console.error('Error fetching items:', err);
  } finally {
    isLoading.value = false;
  }
};



  // Fetch the list of categories
  const fetchCategories = async () => {
    if (categories.value.length > 0) return; // Avoid refetching if already loaded
    isLoading.value = true; // Set loading state to true
    error.value = null; // Reset any previous error

    try {
      // API request to fetch categories
      const response = await axios.get(`${api_base_url}/api/categories/`, {
        withCredentials: true, // Include credentials (cookies) in the request
      });
      categories.value = response.data; // Store the fetched categories
    } catch (err) {
      // Handle error if the request fails
      error.value = 'Failed to fetch categories.';
      showNotification('Items error', `Error fetching categories: ${err.response?.data || err.message}!`, 'error');

    } finally {
      // Set loading to false once the request is done (either success or failure)
      isLoading.value = false;
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

  // Return the state variables and actions to be used in components
  return {
    truncateText,
    userEquipments,
    userEditableEquipmentsIds,
    equipments,
    categories,
    selectedEquipment,
    isLoading,
    error,
    fetchEquipments,
    fetchUserEquipments,
    fetchUserEditableEquipments,
    fetchCategories,
    getEquipmentById,
  };
});
