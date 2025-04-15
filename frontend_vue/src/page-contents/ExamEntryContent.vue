<template>
  <div class="container-fluid d-flex flex-column align-items-center justify-content-center">
    <h1 class="fw-bold m-3 text-shadow">TYT - AYT Deneme Netleri</h1>

    <!-- API'den veri yüklenene kadar -->
    <div v-if="!examData" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Yükleniyor...</span>
      </div>
      <p class="text-muted mt-2">Sınav bilgileri alınıyor...</p>
    </div>

    <!-- ExamForm bileşenini burada kullanıyoruz -->
    <ExamForm v-else :examData="examData" @submit="sendDataToBackend" />

    <!-- Kullanıcıya geri bildirim mesajı -->
    <div v-if="responseMessage" class="alert mt-3 w-50 text-center" :class="responseClass">
      {{ responseMessage }}
    </div>
  </div>
</template>

<script>
import ExamForm from "../components/ExamForm.vue";

export default {
  components: { ExamForm },
  data() {
    return {
      examData: null,
      responseMessage: "",
      responseClass: "",
      token: localStorage.getItem("jwt_token") || "",
    };
  },
  async created() {
    const examId = this.$route.params.id;
    if (examId !== "new") {
      try {
        const response = await fetch("http://localhost:3000/api/exam/exam-details", {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${this.token}` },
          body: JSON.stringify({ exam_id: examId }),
        });
        const result = await response.json();
        console.log("Gelen sınav verisi:", result);

        if (response.ok && result) {
          this.examData = {
            id: result.id || "",
            name: result.name || "Bilinmeyen Sınav",
            date: result.date || new Date().toISOString().split("T")[0],
            results: result.results || {},
          };
        }
      } catch (error) {
        console.error("Sınav verisi alınırken hata oluştu:", error);
      }
    }
  },
  methods: {
    async sendDataToBackend(results) {
      let examId = this.$route.params.id;

      if (examId === "new") {
        try {
          const response = await fetch("http://localhost:3000/api/exam/add", {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${this.token}` },
            body: JSON.stringify(results),
          });
          const result = await response.json();
          if (response.ok) {
            examId = result.examId;
            this.$router.replace(`/deneme-gir/deneme${examId}`);
          } else {
            this.responseMessage = result.error || "Bir hata oluştu!";
            this.responseClass = "alert-danger";
          }
        } catch (error) {
          this.responseMessage = "Bağlantı hatası!";
          this.responseClass = "alert-danger";
        }
      } else {
        try {
          const response = await fetch("http://localhost:3000/api/exam/edit-exam", {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${this.token}` },
            body: JSON.stringify({ exam_id: examId, ...results }),
          });

          const result = await response.json();
          if (response.ok) {
            this.responseMessage = "Veriler başarıyla güncellendi!";
            this.responseClass = "alert-success";
          } else {
            this.responseMessage = result.error || "Bir hata oluştu!";
            this.responseClass = "alert-danger";
          }
        } catch (error) {
          this.responseMessage = "Bağlantı hatası!";
          this.responseClass = "alert-danger";
        }
      }
    },
  },
};
</script>

<style scoped>
.text-shadow {
  text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
}
</style>
