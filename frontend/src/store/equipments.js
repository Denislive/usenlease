import { defineStore } from 'pinia';
import axios from 'axios';
import { ref } from 'vue';

export const useEquipmentsStore = defineStore('equipments', () => {
  const equipments = ref([]);
  const categories = ref([]);
  const selectedEquipment = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  const fetchEquipments = async () => {
    if (equipments.value.length > 0) return; // Avoid refetching if already loaded
    isLoading.value = true;
    error.value = null;

    try {
      const response = await axios.get('http://127.0.0.1:8000/api/equipments/', {
        withCredentials: true,
      });
      equipments.value = response.data;
      console.log('Fetched Equipments:', equipments.value);
    } catch (err) {
      error.value = 'Failed to fetch equipments.';
      console.error(err);
    } finally {
      isLoading.value = false;
    }
  };

  const fetchCategories = async () => {
    if (categories.value.length > 0) return; // Avoid refetching if already loaded
    isLoading.value = true;
    error.value = null;

    try {
      const response = await axios.get('http://127.0.0.1:8000/api/categories/', {
        withCredentials: true,
      });
      categories.value = response.data;
      console.log('Fetched Categories:', categories.value);
    } catch (err) {
      error.value = 'Failed to fetch categories.';
      console.error('Error fetching categories:', err.response ? err.response.data : err);
    } finally {
      isLoading.value = false;
    }
  };

  const getEquipmentById = async (id) => {
    // Check if the equipment is already in the list to avoid unnecessary API calls
    const equipment = equipments.value.find((item) => item.id === id);
    if (equipment) {
      selectedEquipment.value = equipment;
    } else {
      isLoading.value = true;
      error.value = null;
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/equipments/${id}/`, {
          withCredentials: true,
        });
        selectedEquipment.value = response.data;
        console.log('Fetched Equipment by ID:', selectedEquipment.value);
      } catch (err) {
        error.value = `Failed to fetch equipment with ID ${id}.`;
        console.error(err);
      } finally {
        isLoading.value = false;
      }
    }
  };

  return {
    equipments,
    categories,
    selectedEquipment,
    isLoading,
    error,
    fetchEquipments,
    fetchCategories,
    getEquipmentById,
  };
});
