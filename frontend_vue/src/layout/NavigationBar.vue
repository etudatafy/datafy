<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-success ps-4 fixed-top">
    <div class="container-fluid d-flex align-items-center">
      <span v-if="title" class="navbar-text fs-4 fw-semibold me-auto">
        {{ title }}
      </span>
      <div class="d-flex align-items-center">
        <template v-if="isAuth">
          <router-link to="/ana-sayfa" class="nav-link me-3">
            <i class="bi bi-house-fill fs-4"></i>
          </router-link>
          <router-link to="/yapay-zeka-yardim" class="nav-link me-3">
            <i class="bi bi-robot fs-4"></i>
          </router-link>
          <router-link to="/takvim" class="nav-link me-3">
            <i class="bi bi-calendar-event-fill fs-4"></i>
          </router-link>
          <router-link to="/gelisim-analiz" class="nav-link me-3">
            <i class="bi bi-bar-chart-line-fill fs-4"></i>
          </router-link>
          <button @click="showLogoutModal = true" class="btn nav-link p-0">
            <i class="bi bi-box-arrow-right fs-4"></i>
          </button>
        </template>
        <template v-else>
          <router-link to="/giris-yap" class="nav-link me-3">Giriş Yap</router-link>
          <router-link to="/kayit-ol" class="nav-link">Kayıt Ol</router-link>
        </template>
      </div>
    </div>

    <LogoutWarning
      :show="showLogoutModal"
      @close="showLogoutModal = false"
      @confirm="confirmLogout"
    />
  </nav>
</template>

<script>
import LogoutWarning from '../warnings/LogoutWarning.vue';

export default {
  name: 'NavigationBar',
  components: { LogoutWarning },
  props: {
    title: { type: String, default: '' }
  },
  data() {
    return { showLogoutModal: false }
  },
  computed: {
    isAuth() {
      return !!localStorage.getItem('jwt_token');
    }
  },
  methods: {
    confirmLogout() {
      localStorage.removeItem('jwt_token');
      this.showLogoutModal = false;
      this.$router.push('/giris-yap');
    }
  }
}
</script>

<style scoped>
.navbar { height: 60px; }
.nav-link { color: white; }
.nav-link:hover { color: #e0e0e0; }
</style>
