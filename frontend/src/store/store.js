import { createStore } from 'vuex';
import { useEquipmentsStore } from '@/store/equipments';

const store = createStore({
  state: () => ({
    searchQuery: '', // Stores the user's search input
  }),

  getters: {
    getSearchQuery: (state) => state.searchQuery, // Retrieve the search query

    getFilteredEquipments: (state) => {
      const equipmentStore = useEquipmentsStore();
      const allEquipments = equipmentStore.equipments || [];
      const query = state.searchQuery.trim().toLowerCase();

      if (!query) return allEquipments; // Return all equipment if no search

      return allEquipments.filter((equipment) =>
        equipment.name.toLowerCase().includes(query)
      );
    },
  },

  mutations: {
    setSearchQuery(state, query) {
      state.searchQuery = query; // Update search input state
    },
  },

  actions: {
    setSearchQuery({ commit }, query) {
      commit('setSearchQuery', query); // Update search query
    },
  },
});

export default store;
