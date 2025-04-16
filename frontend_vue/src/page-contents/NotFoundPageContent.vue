<template>
  <div class="card shadow-lg border-0">
    <div class="card-body text-center py-5">
      <i class="bi bi-exclamation-triangle-fill display-1 text-warning mb-5"></i>
      <h2 class="card-title text-danger fw-bold mb-3 mt-3">Sayfa Bulunamadı</h2>
      <p class="card-text fs-5 mb-2">{{ message }}</p>
      <p class="text-muted">
        Yaklaşık <span class="fw-semibold">{{ countdown }}</span> saniye içinde
        yönlendiriliyorsunuz...
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundPageContent',
  data() {
    return {
      countdown: 10,
      message: '',
      redirectTo: '/'
    }
  },
  created() {
    const token = localStorage.getItem('jwt_token')
    if (token) {
      this.message = 'Geçersiz bir sayfaya erişmeye çalıştınız. Ana sayfaya yönlendiriliyorsunuz.'
      this.redirectTo = '/ana-sayfa'
    } else {
      this.message = 'Geçersiz bir sayfaya erişmeye çalıştınız. Giriş sayfasına yönlendiriliyorsunuz.'
      this.redirectTo = '/giris-yap'
    }
    this._timer = setInterval(() => {
      this.countdown--
      if (this.countdown <= 0) {
        clearInterval(this._timer)
        this.$router.replace(this.redirectTo)
      }
    }, 1000)
  },
  beforeUnmount() {
    clearInterval(this._timer)
  }
}
</script>
