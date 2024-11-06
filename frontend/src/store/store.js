import { createStore } from 'vuex';
import { reactive } from 'vue';

// Create a store using the Composition API
const store = createStore({
  state: () => ({
    user: null, // For user authentication
    loginError: '',
    searchQuery: '', // New state for the search query
  }),
  getters: {
    isAuthenticated: (state) => !!state.user, // Check if user is authenticated
    getSearchQuery: (state) => state.searchQuery, // Get the current search query
  },
  mutations: {
    setUser(state, user) {
      state.user = user; // Set user state
    },
    setLoginError(state, error) {
      state.loginError = error; // Set login error state
    },
    setSearchQuery(state, query) {
      state.searchQuery = query; // Set the search query
    },
  },
  actions: {
    async login({ commit }, { email, password }) {
      try {
        // Perform the login logic here (e.g., API call)
        const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/login/`, {
          email,
          password,
        });

        // Set the user in the state after successful login
        commit('setUser', response.data.user); // Adjust according to your response structure
      } catch (error) {
        commit('setLoginError', error.response.data.message || 'Login failed.'); // Set error message
      }
    },
    setSearchQuery({ commit }, query) {
      commit('setSearchQuery', query); // Action to set the search query
    },
  },
});

export default store;
