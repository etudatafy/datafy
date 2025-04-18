// frontend/src/store.js

import { createStore } from 'vuex';

const backendUrl =
  typeof process !== 'undefined' &&
  process.env &&
  process.env.BACKEND_URL
    ? process.env.BACKEND_URL
    : 'http://localhost:3000';

const store = createStore({
  state() {
    return {
      user: null,
      apiBase: backendUrl,   // <<< burada environment ya da fallback URL
    };
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
    },
  },
  actions: {
    login({ commit }, user) {
      commit('setUser', user);
    },
    logout({ commit }) {
      commit('setUser', null);
    },
  },
  getters: {
    isAuthenticated(state) {
      return !!state.user;
    },
    apiBase(state) {
      return state.apiBase;
    },
  },
});

export default store;
