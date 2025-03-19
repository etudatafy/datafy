<template>
  <div class="container-fluid vh-100 d-flex flex-column align-items-center justify-content-center bg-success-subtle">
    <h1 class="text-center text-dark fw-bold mb-4">📅 Takvim</h1>

    <div class="card shadow-lg p-4 bg-light w-75">
      <div class="d-flex justify-content-between align-items-center">
        <h3 class="fw-bold text-dark">⏳ Gelecek Sınavlar</h3>
        <button class="btn btn-success" @click="showFutureModal = true">
          <i class="bi bi-plus-circle"></i> Sınav Ekle
        </button>
      </div>
      <ul v-if="futureExams.length" class="list-group mt-3">
        <li v-for="exam in futureExams" :key="exam.id" class="list-group-item d-flex justify-content-between align-items-center">
          <span class="fw-bold">{{ exam.name }}</span> 
          <span class="text-muted">{{ exam.date }}</span>
          <button class="btn btn-danger btn-sm" @click="deleteExam(exam.id)">
            <i class="bi bi-trash"></i> Sil
          </button>
        </li>
      </ul>
      <p v-else class="text-muted text-center mt-3">Henüz bir sınav eklenmedi.</p>
    </div>

    <div class="card shadow-lg p-4 bg-light mt-4 w-75">
      <div class="d-flex justify-content-between align-items-center">
        <h3 class="fw-bold text-dark">📌 Geçmiş Sınavlar</h3>
        <button class="btn btn-success" @click="showPastModal = true">
          <i class="bi bi-plus-circle"></i> Sınav Ekle
        </button>
      </div>
      <ul v-if="pastExams.length" class="list-group mt-3">
        <li v-for="exam in pastExams" :key="exam.id" class="list-group-item d-flex justify-content-between align-items-center">
          <span class="fw-bold">{{ exam.name }}</span> 
          <span class="text-muted">{{ exam.date }}</span>
          <div>
            <button class="btn btn-danger btn-sm me-2" @click="deleteExam(exam.id)">
              <i class="bi bi-trash"></i> Sil
            </button>
            <router-link :to="'/deneme-gir/' + exam.id" class="btn btn-success btn-sm">
              <i class="bi bi-pencil-square"></i> Düzenle
            </router-link>
          </div>
        </li>
      </ul>
      <p v-else class="text-muted text-center mt-3">Henüz bir sınav eklenmedi.</p>
    </div>

    <div v-if="showFutureModal || showPastModal" class="modal d-block bg-dark bg-opacity-50">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Yeni Sınav Ekle</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <label class="form-label">Sınav İsmi:</label>
            <input type="text" v-model="newExam.name" class="form-control" placeholder="Deneme Adı" />

            <label class="form-label mt-2">Tarih:</label>
            <input type="date" v-model="newExam.date" class="form-control" />
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">İptal</button>
            <button class="btn btn-success" @click="addExam">Ekle</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showFutureModal: false,
      showPastModal: false,
      newExam: { name: "", date: "" },
      exams: [],
      token: localStorage.getItem("jwt_token") || "",
    };
  },
  computed: {
    futureExams() {
      return this.exams
        .filter((exam) => new Date(exam.date) >= new Date())
        .sort((a, b) => new Date(a.date) - new Date(b.date)); // En yakından en uzağa sıralama
    },
    pastExams() {
      return this.exams
        .filter((exam) => new Date(exam.date) < new Date())
        .sort((a, b) => new Date(b.date) - new Date(a.date)); // En yakından en uzağa sıralama
    },
  },
  methods: {
    async fetchExams() {
      try {
        const response = await fetch("http://localhost:3000/api/exam/fetch-exams", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        const result = await response.json();
        if (response.ok) this.exams = result;
      } catch (error) {
        console.error("Sınavları alırken hata oluştu:", error);
      }
    },
    async addExam() {
      if (!this.newExam.name || !this.newExam.date) return alert("Tüm alanları doldurun!");
      try {
        const response = await fetch("http://localhost:3000/api/exam/add", {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${this.token}` },
          body: JSON.stringify(this.newExam),
        });
        const result = await response.json();
        if (response.ok) {
          this.fetchExams();
          this.closeModal();
          if (new Date(this.newExam.date) < new Date()) {
            this.$router.push(`/deneme-gir/deneme${result.examId}`);
          }
        }
      } catch (error) {
        console.error("Sınav eklenirken hata:", error);
      }
    },
    async deleteExam(examId) {
      if (!confirm("Bu sınavı silmek istediğinize emin misiniz?")) return;

      try {
        const response = await fetch("http://localhost:3000/api/exam/delete-exam", {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${this.token}` },
          body: JSON.stringify({ exam_id: examId }),
        });
        const result = await response.json();
        if (response.ok) {
          this.exams = this.exams.filter((exam) => exam.id !== examId);
        } else {
          console.error("Sınav silinirken hata:", result.error);
        }
      } catch (error) {
        console.error("Bağlantı hatası:", error);
      }
    },
    closeModal() {
      this.showFutureModal = false;
      this.showPastModal = false;
      this.newExam = { name: "", date: "" };
    },
  },
  mounted() {
    this.fetchExams();
  },
};
</script>
