import { createStore } from 'vuex';
import axios from 'axios';

const api_base_url = import.meta.env.VITE_API_BASE_URL;

const store = createStore({
  state: () => ({
    searchQuery: '', // New state for the search query
    filteredEquipments: [], // State for filtered equipments
    categories: [], // State for categories
    equipments: [] // State for all equipments
  }),
  getters: {
    getSearchQuery: (state) => state.searchQuery, // Get the current search query
    getFilteredEquipments: (state) => state.filteredEquipments, // Get the filtered equipments
    getCategories: (state) => state.categories, // Get the categories
    getEquipments: (state) => state.equipments // Get all equipments
  },
  mutations: {
    setSearchQuery(state, query) {
      state.searchQuery = query; // Set the search query
    },
    setFilteredEquipments(state, equipments) {
      state.filteredEquipments = equipments; // Set the filtered equipments
    },
    setCategories(state, categories) {
      state.categories = categories; // Set the categories
    },
    setEquipments(state, equipments) {
      state.equipments = equipments; // Set all equipments
    }
  },
  actions: {
    setSearchQuery({ commit }, query) {
      commit('setSearchQuery', query); // Action to set the search query
    },
    setFilteredEquipments({ commit }, equipments) {
      commit('setFilteredEquipments', equipments); // Action to set the filtered equipments
    },
    fetchCategories: async ({ commit }) => {
      try {
        const response = await axios.get(`${api_base_url}/api/categories/`);
        commit('setCategories', response.data);
      } catch (error) {
        console.error('Error fetching category data:', error);
      }
    },
    fetchEquipments: async ({ commit }) => {
      try {
        const response = await axios.get(`${api_base_url}/api/equipments/`);
        commit('setEquipments', response.data);
      } catch (error) {
        console.error('Error fetching equipment data:', error);
      }
    }
  }
});

export default store;
