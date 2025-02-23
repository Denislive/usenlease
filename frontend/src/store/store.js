import { createStore } from 'vuex';
import { useEquipmentsStore } from '@/store/equipments';

const store = createStore({
  state: () => ({
    searchQuery: '', // New state for the search query
    filteredEquipments: [], // State for filtered equipments
  }),
  getters: {
    getSearchQuery: (state) => state.searchQuery, // Get the current search query
    getFilteredEquipments: (state) => state.filteredEquipments, // Get the filtered equipments
    getCategories: () => {
      const equipmentStore = useEquipmentsStore();
      return equipmentStore.categories;
    },
    getEquipments: () => {
      const equipmentStore = useEquipmentsStore();
      return equipmentStore.equipments;
    },
  },
  mutations: {
    setSearchQuery(state, query) {
      state.searchQuery = query; // Set the search query
    },
    setFilteredEquipments(state, equipments) {
      state.filteredEquipments = equipments; // Set the filtered equipments
    },
  },
  actions: {
    setSearchQuery({ commit }, query) {
      commit('setSearchQuery', query);
    },
    setFilteredEquipments({ commit }, equipments) {
      commit('setFilteredEquipments', equipments);
    },
  },
});

export default store;
