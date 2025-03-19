<template>
  <div class="container-fluid d-flex justify-content-center align-items-center vh-100 bg-success-subtle">
    <div class="card p-4 shadow-lg w-50">
      <h2 class="text-center text-success fw-bold mb-4">Giriş Yap</h2>
      <form @submit.prevent="login">
        <div class="mb-3">
          <label for="email" class="form-label text-success">E-posta:</label>
          <input type="email" id="email" class="form-control border-success" v-model="form.email" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label text-success">Şifre:</label>
          <input type="password" id="password" class="form-control border-success" v-model="form.password" required />
        </div>
        <button type="submit" class="btn btn-success w-100" :disabled="loading">
          <span v-if="loading">
            <span class="spinner-border spinner-border-sm"></span> Giriş Yapılıyor...
          </span>
          <span v-else>Giriş Yap</span>
        </button>
      </form>

      <!-- Kayıt Ol Butonu -->
      <div class="text-center mt-3">
        <p class="text-dark">Hesabınız yok mu? 
          <router-link to="/kayit-ol" class="text-decoration-none fw-semibold text-success">
            Kayıt olun.
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        email: '',
        password: '',
      },
      loading: false, // Yükleme göstergesi için
    };
  },
  methods: {
    async login() {
      this.loading = true;
      try {
        const response = await axios.post('http://localhost:3000/api/auth/login', {
          email: this.form.email,
          password: this.form.password,
        });

        // JWT token'ı Local Storage'e kaydet
        const token = response.data.token;
        localStorage.setItem('jwt_token', token);

        alert('Giriş başarılı!');
        console.log('Sunucu Yanıtı:', response.data);
        this.$router.push('/ana-sayfa');
      } catch (error) {
        const errorMessage =
          error.response?.data?.message || 'Giriş sırasında hata oluştu.';
        alert(errorMessage);
        console.error('Hata:', error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
