<template>
  <div class="container-fluid d-flex justify-content-center align-items-center vh-100">
    <div class="card p-4 shadow-lg w-50">
      <h2 class="text-center text-success fw-bold mb-4">Kayıt Ol</h2>
      <form @submit.prevent="register">
        <div class="mb-3">
          <label for="username" class="form-label text-success">Kullanıcı Adı:</label>
          <input type="text" id="username" class="form-control border-success" v-model="form.username" required />
        </div>
        <div class="mb-3">
          <label for="email" class="form-label text-success">E-posta:</label>
          <input type="email" id="email" class="form-control border-success" v-model="form.email" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label text-success">Şifre:</label>
          <input type="password" id="password" class="form-control border-success" v-model="form.password" required />
        </div>
        <div class="mb-3">
          <label for="confirmPassword" class="form-label text-success">Şifre Doğrulama:</label>
          <input type="password" id="confirmPassword" class="form-control border-success" v-model="form.confirmPassword" required />
        </div>
        <button type="submit" class="btn btn-success w-100">Kayıt Ol</button>
      </form>

      <!-- Giriş Yap Butonu -->
      <div class="text-center mt-3">
        <p class="text-dark">Hesabınız var mı? 
          <router-link to="/giris-yap" class="text-decoration-none fw-semibold text-success">
            Giriş yapın.
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
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
      },
    };
  },
  methods: {
    async register() {
      if (this.form.password !== this.form.confirmPassword) {
        alert('Şifreler eşleşmiyor!');
        return;
      }

      try {
        const response = await axios.post('http://localhost:3000/api/auth/register', {
          username: this.form.username,
          email: this.form.email,
          password: this.form.password,
        });

        alert('Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...');
        console.log('Sunucu Yanıtı:', response.data);
        this.$router.push('/giris-yap');
      } catch (error) {
        const errorMessage =
          error.response?.data?.message || 'Kayıt sırasında hata oluştu.';
        alert(errorMessage);
        console.error('Hata:', error);
      }
    },
  },
};
</script>
