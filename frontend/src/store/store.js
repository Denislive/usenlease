import { createStore } from 'vuex';

// Create a store using the Composition API
const store = createStore({
  state: () => ({

    searchQuery: '', // New state for the search query
  }),
  getters: {
    getSearchQuery: (state) => state.searchQuery, // Get the current search query
  },
  mutations: {
   
    setSearchQuery(state, query) {
      state.searchQuery = query; // Set the search query
    },
  },
  actions: {
    setSearchQuery({ commit }, query) {
      commit('setSearchQuery', query); // Action to set the search query
    },
  },
});

export default store;
