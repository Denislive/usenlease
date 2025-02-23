import { createStore } from 'vuex';
import axios from 'axios';

const api_base_url = import.meta.env.VITE_API_BASE_URL;

const store = createStore({
  state: () => ({
    searchQuery: '',
    filteredEquipments: [],
    categories: [],
    equipments: [],
  }),
  getters: {
    getSearchQuery: (state) => state.searchQuery,
    getFilteredEquipments: (state) => state.filteredEquipments,
    getCategories: (state) => state.categories,
    getEquipments: (state) => state.equipments,
  },
  mutations: {
    setSearchQuery(state, query) {
      console.log('STORE - Mutation [setSearchQuery]:', query);
      state.searchQuery = query;
    },
    setFilteredEquipments(state, equipments) {
      console.log('STORE - Mutation [setFilteredEquipments]:', equipments);
      state.filteredEquipments = equipments;
    },
    setCategories(state, categories) {
      console.log('STORE - Mutation [setCategories]:', categories);
      state.categories = Array.isArray(categories) ? categories : []; // Ensure valid array
    },
    setEquipments(state, equipments) {
      console.log('STORE - Mutation [setEquipments]:', equipments);
      state.equipments = Array.isArray(equipments) ? equipments : []; // Ensure valid array
    },
  },
  actions: {
    async fetchCategories({ commit }) {
      try {
        console.log('STORE - Action [fetchCategories] - Fetching categories...');
        const response = await axios.get(`${api_base_url}/api/categories/`);
        if (response.data) {
          console.log('STORE - Action [fetchCategories] - Received categories:', response.data);
          commit('setCategories', response.data);
        } else {
          console.warn('STORE - Action [fetchCategories] - No categories received!');
          commit('setCategories', []);
        }
      } catch (error) {
        console.error('STORE - Error fetching categories:', error);
        commit('setCategories', []); // Reset categories on error
      }
    },
    async fetchEquipments({ commit }) {
      try {
        console.log('STORE - Action [fetchEquipments] - Fetching equipments...');
        const response = await axios.get(`${api_base_url}/api/equipments/`);
        if (response.data) {
          console.log('STORE - Action [fetchEquipments] - Received equipments:', response.data);
          commit('setEquipments', response.data);
        } else {
          console.warn('STORE - Action [fetchEquipments] - No equipments received!');
          commit('setEquipments', []);
        }
      } catch (error) {
        console.error('STORE - Error fetching equipments:', error);
        commit('setEquipments', []); // Reset equipments on error
      }
    },
  },
});

export default store;
