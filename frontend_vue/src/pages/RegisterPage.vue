<template>
  <div class="register-container">
    <h2>Kayıt Ol</h2>
    <form @submit.prevent="register">
      <div>
        <label for="username">Kullanıcı Adı:</label>
        <input type="text" id="username" v-model="form.username" required />
      </div>
      <div>
        <label for="email">E-posta:</label>
        <input type="email" id="email" v-model="form.email" required />
      </div>
      <div>
        <label for="password">Şifre:</label>
        <input type="password" id="password" v-model="form.password" required />
      </div>
      <div>
        <label for="confirmPassword">Şifre Doğrulama:</label>
        <input type="password" id="confirmPassword" v-model="form.confirmPassword" required />
      </div>
      <button type="submit">Kayıt Ol</button>
    </form>
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
        this.$router.push('/login');
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
