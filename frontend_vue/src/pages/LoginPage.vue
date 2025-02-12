<template>
  <div class="login-container">
    <h2>Giriş Yap</h2>
    <form @submit.prevent="login">
      <div>
        <label for="email">E-posta:</label>
        <input type="email" id="email" v-model="form.email" required />
      </div>
      <div>
        <label for="password">Şifre:</label>
        <input type="password" id="password" v-model="form.password" required />
      </div>
      <button type="submit">Giriş Yap</button>
    </form>
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
    };
  },
  methods: {
    async login() {
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
      }
    },
  },
};
</script>
