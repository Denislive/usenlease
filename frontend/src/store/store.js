import { createStore } from 'vuex';
import { useEquipmentsStore } from '@/store/equipments';

const store = createStore({
  state: () => ({
    searchQuery: '',
    filteredEquipments: [],
    categories: [], // Store categories locally
    equipments: [], // Store equipments locally
  }),
  getters: {
    getSearchQuery: (state) => state.searchQuery,
    getFilteredEquipments: (state) => state.filteredEquipments,
    getCategories: (state) => state.categories,
    getEquipments: (state) => state.equipments,
  },
  mutations: {
    setSearchQuery(state, query) {
      state.searchQuery = query;
    },
    setFilteredEquipments(state, equipments) {
      state.filteredEquipments = equipments;
    },
    setCategories(state, categories) {
      state.categories = categories;
    },
    setEquipments(state, equipments) {
      state.equipments = equipments;
    },
  },
  actions: {
    syncWithPinia({ commit }) {
      const equipmentStore = useEquipmentsStore();
      commit('setCategories', equipmentStore.categories);
      commit('setEquipments', equipmentStore.equipments);
    },
    setSearchQuery({ commit }, query) {
      commit('setSearchQuery', query);
    },
    setFilteredEquipments({ commit }, equipments) {
      commit('setFilteredEquipments', equipments);
    },
  },
});

export default store;
