<template>
  <div class="container-fluid d-flex flex-column align-items-center justify-content-center vh-100 bg-success-subtle">
    <!-- Ana Sayfa Başlığı -->
    <h1 class="fw-bold text-dark mb-4" style="font-size: 2.5rem; text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);">
      Ana Sayfa
    </h1>

    <!-- Sayaç Kısmı -->
    <div class="card shadow-lg text-center mb-4 p-4 w-50">
      <h2 class="fw-bold text-muted" style="font-size: 1.8rem;">
        YKS'ye Kalan Süre
      </h2>
      <p class="fs-4 fw-semibold text-danger mt-2" id="countdown"></p>
    </div>

    <!-- Router Linkleri -->
    <div class="row w-50 g-3">
      <div class="col-6">
        <router-link to="/yapay-zeka-yardim" class="btn btn-success w-100 py-3 d-flex align-items-center justify-content-center">
          <i class="bi bi-robot fs-4 me-2"></i> <span>Yapay Zeka Yardım</span>
        </router-link>
      </div>
      <div class="col-6">
        <router-link to="/gelisim-analiz" class="btn btn-primary w-100 py-3 d-flex align-items-center justify-content-center">
          <i class="bi bi-bar-chart-line fs-4 me-2"></i> <span>Gelişim Analizi</span>
        </router-link>
      </div>
      <div class="col-6">
        <router-link to="/canli-destek" class="btn btn-danger w-100 py-3 d-flex align-items-center justify-content-center">
          <i class="bi bi-headset fs-4 me-2"></i> <span>Canlı Destek</span>
        </router-link>
      </div>
      <div class="col-6">
        <router-link to="/ayarlar" class="btn btn-secondary w-100 py-3 d-flex align-items-center justify-content-center">
          <i class="bi bi-gear fs-4 me-2"></i> <span>Ayarlar</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  mounted() {
    this.startCountdown();
  },
  methods: {
    startCountdown() {
      const examDate = new Date("June 15, 2025 10:00:00").getTime();
      const countdownElement = document.getElementById("countdown");

      const updateCountdown = () => {
        const now = new Date().getTime();
        const timeLeft = examDate - now;

        if (timeLeft > 0) {
          const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
          const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

          countdownElement.innerText = `${days} gün ${hours} saat ${minutes} dakika ${seconds} saniye`;
        } else {
          countdownElement.innerText = "Sınav zamanı!";
        }
      };

      updateCountdown();
      setInterval(updateCountdown, 1000);
    }
  }
};
</script>
