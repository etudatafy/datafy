<!-- src/pages/CalenderPage.vue -->
<template>
  <PageLayout navbarText="Takvim">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-12 col-md-10 col-lg-8">
          <h1 class="text-center text-dark fw-bold mb-4">📅 Takvim</h1>

          <!-- Gelecek Sınavlar -->
          <div class="card shadow mb-4">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h3 class="card-title fw-bold mb-0">⏳ Gelecek Sınavlar</h3>
                <button class="btn btn-success" @click="showFutureModal = true">
                  <i class="bi bi-plus-circle me-1"></i> Sınav Ekle
                </button>
              </div>
              <ul v-if="futureExams.length" class="list-group list-group-flush">
                <li
                  v-for="exam in futureExams"
                  :key="exam.id"
                  class="list-group-item d-flex align-items-center"
                >
                  <!-- 1. kolon: isim -->
                  <div class="flex-fill">
                    <span class="fw-bold">{{ exam.name }}</span>
                  </div>
                  <!-- 2. kolon: tarih (ortalanmış) -->
                  <div class="flex-fill text-center text-muted">
                    {{ exam.date }}
                  </div>
                  <!-- 3. kolon: sil butonu -->
                  <div class="flex-fill text-end">
                    <button
                      class="btn btn-danger btn-sm"
                      @click="deleteExam(exam.id)"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </li>
              </ul>
              <p v-else class="text-muted text-center">Henüz bir sınav eklenmedi.</p>
            </div>
          </div>

          <!-- Geçmiş Sınavlar -->
          <div class="card shadow">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h3 class="card-title fw-bold mb-0">📌 Geçmiş Sınavlar</h3>
                <button class="btn btn-success" @click="showPastModal = true">
                  <i class="bi bi-plus-circle me-1"></i> Sınav Ekle
                </button>
              </div>
              <ul v-if="pastExams.length" class="list-group list-group-flush">
                <li
                  v-for="exam in pastExams"
                  :key="exam.id"
                  class="list-group-item d-flex align-items-center"
                >
                  <div class="flex-fill">
                    <span class="fw-bold">{{ exam.name }}</span>
                  </div>
                  <div class="flex-fill text-center text-muted">
                    {{ exam.date }}
                  </div>
                  <div class="flex-fill text-end">
                    <button
                      class="btn btn-danger btn-sm me-2"
                      @click="deleteExam(exam.id)"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                    <router-link
                      :to="`/deneme-gir/${exam.id}`"
                      class="btn btn-success btn-sm"
                    >
                      <i class="bi bi-pencil-square"></i> Düzenle
                    </router-link>
                  </div>
                </li>
              </ul>
              <p v-else class="text-muted text-center">Henüz bir sınav eklenmedi.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal aynı kaldı -->
    <div v-if="showFutureModal || showPastModal">
      <div class="modal fade show" style="display: block;" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Yeni Sınav Ekle</h5>
              <button type="button" class="btn-close" @click="closeModal"></button>
            </div>
            <div class="modal-body">
              <label class="form-label">Sınav İsmi:</label>
              <input
                type="text"
                v-model="newExam.name"
                class="form-control"
                placeholder="Deneme Adı"
              />
              <label class="form-label mt-3">Tarih:</label>
              <input
                type="date"
                v-model="newExam.date"
                class="form-control"
              />
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="closeModal">
                İptal
              </button>
              <button class="btn btn-success" @click="addExam">
                Ekle
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
  </PageLayout>
</template>

<script>
import PageLayout from '../layout/PageLayout.vue';

export default {
  name: 'CalenderPageContent',
  components: { PageLayout },
  data() {
    return {
      showFutureModal: false,
      showPastModal: false,
      newExam: { name: '', date: '' },
      exams: [],
      token: localStorage.getItem('jwt_token') || '',
    };
  },
  computed: {
    futureExams() {
      return this.exams
        .filter(e => new Date(e.date) >= new Date())
        .sort((a, b) => new Date(a.date) - new Date(b.date));
    },
    pastExams() {
      return this.exams
        .filter(e => new Date(e.date) < new Date())
        .sort((a, b) => new Date(b.date) - new Date(a.date));
    },
  },
  methods: {
    async fetchExams() {
      try {
        const res = await fetch('http://localhost:3000/api/exam/fetch-exams', {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        const data = await res.json();
        if (res.ok) this.exams = data;
      } catch (err) {
        console.error(err);
      }
    },
    async addExam() {
      if (!this.newExam.name || !this.newExam.date) {
        return alert('Tüm alanları doldurun!');
      }
      try {
        const res = await fetch('http://localhost:3000/api/exam/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`,
          },
          body: JSON.stringify(this.newExam),
        });
        if (res.ok) {
          this.fetchExams();
          this.closeModal();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async deleteExam(id) {
      if (!confirm('Silmek istediğinize emin misiniz?')) return;
      try {
        const res = await fetch('http://localhost:3000/api/exam/delete-exam', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`,
          },
          body: JSON.stringify({ exam_id: id }),
        });
        if (res.ok) this.exams = this.exams.filter(e => e.id !== id);
      } catch (err) {
        console.error(err);
      }
    },
    closeModal() {
      this.showFutureModal = false;
      this.showPastModal = false;
      this.newExam = { name: '', date: '' };
    },
  },
  mounted() {
    this.fetchExams();
  },
};
</script>

<style scoped>
.modal-backdrop {
  z-index: 1040;
}
.modal {
  z-index: 1050;
}
</style>
