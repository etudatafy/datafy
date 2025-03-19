<template>
  <div class="card shadow-lg p-4 w-50">
    <h2 class="text-center fw-bold text-success">TYT - AYT Net Girişi</h2>

    <div class="mb-3">
      <label for="examName" class="form-label fw-semibold">Deneme Adı:</label>
      <input type="text" v-model="examName" class="form-control" id="examName" placeholder="Deneme adını girin" />
    </div>

    <div class="mb-3">
      <label for="examDate" class="form-label fw-semibold">Deneme Tarihi:</label>
      <input type="date" v-model="examDate" class="form-control" id="examDate" />
    </div>

    <div v-for="(exam, index) in exams" :key="index" class="mt-4">
      <h3 class="fw-bold">{{ exam.title }}</h3>
      <div v-for="(subject, sIndex) in exam.subjects" :key="sIndex" class="mb-2">
        <label :for="subject.name" class="form-label">{{ subject.label }}:</label>
        <div class="input-group">
          <input
            type="number"
            v-model.number="subject.score"
            class="form-control"
            :id="subject.name"
            :name="subject.name"
            min="0"
            :max="subject.max"
            step="0.25"
          />
          <span class="input-group-text">/ {{ subject.max }}</span>
        </div>
      </div>
    </div>

    <div class="d-flex justify-content-between mt-3">
      <button v-if="examId" class="btn btn-danger" @click="deleteExam">Sil</button>
      <button class="btn btn-success ms-auto" @click="submitScores">Kaydet</button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    examData: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      examId: null,
      examName: "",
      examDate: "",
      exams: [
        {
          title: "TYT",
          subjects: [
            { name: "turkce", label: "Türkçe", score: 0, max: 40 },
            { name: "sosyal", label: "Sosyal Bilimler", score: 0, max: 20 },
            { name: "matematik", label: "Matematik", score: 0, max: 40 },
            { name: "fen", label: "Fen Bilimleri", score: 0, max: 20 },
          ],
        },
        {
          title: "AYT",
          subjects: [
            { name: "matematik_ayt", label: "Matematik", score: 0, max: 40 },
            { name: "fizik", label: "Fizik", score: 0, max: 14 },
            { name: "kimya", label: "Kimya", score: 0, max: 13 },
            { name: "biyoloji", label: "Biyoloji", score: 0, max: 13 },
            { name: "edebiyat", label: "Türk Dili ve Edebiyatı", score: 0, max: 24 },
            { name: "tarih_1", label: "Tarih-1", score: 0, max: 10 },
            { name: "cografya_1", label: "Coğrafya-1", score: 0, max: 6 },
            { name: "tarih_2", label: "Tarih-2", score: 0, max: 11 },
            { name: "cografya_2", label: "Coğrafya-2", score: 0, max: 11 },
            { name: "felsefe", label: "Felsefe Grubu", score: 0, max: 12 },
            { name: "din", label: "Din Kültürü", score: 0, max: 6 },
          ],
        },
      ],
    };
  },
  watch: {
    examData: {
      handler(newVal) {
        if (newVal) {
          this.examId = newVal.id || null;
          this.examName = newVal.name || "";
          this.examDate = newVal.date || "";

          if (newVal.results) {
            this.exams.forEach((exam) => {
              if (newVal.results[exam.title]) {
                exam.subjects.forEach((subject) => {
                  if (newVal.results[exam.title][subject.name] !== undefined) {
                    subject.score = newVal.results[exam.title][subject.name];
                  }
                });
              }
            });
          }
        }
      },
      immediate: true,
      deep: true,
    },
  },
  methods: {
    async submitScores() {
      if (!this.examName || !this.examDate) {
        alert("Lütfen deneme ismini ve tarihini giriniz.");
        return;
      }

      const results = {
        exam_id: this.examId,
        examName: this.examName,
        examDate: this.examDate,
        exams: this.exams.map((exam) => ({
          title: exam.title,
          subjects: exam.subjects.map((subject) => ({
            name: subject.name,
            score: subject.score,
          })),
        })),
      };

      try {
        const response = await fetch("http://localhost:3000/api/exam/edit-exam", {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("jwt_token")}` },
          body: JSON.stringify(results),
        });

        const result = await response.json();
        if (response.ok) {
          alert("Sınav başarıyla güncellendi!");
          this.$router.push("/takvim");
        } else {
          alert(result.error || "Bir hata oluştu!");
        }
      } catch (error) {
        alert("Bağlantı hatası!");
      }
    },
    async deleteExam() {
      if (!confirm("Bu sınavı silmek istediğinize emin misiniz?")) return;

      try {
        const response = await fetch("http://localhost:3000/api/exam/delete-exam", {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("jwt_token")}` },
          body: JSON.stringify({ exam_id: this.examId }),
        });

        const result = await response.json();
        if (response.ok) {
          alert("Sınav başarıyla silindi!");
          this.$router.push("/takvim");
        } else {
          alert(result.error || "Sınav silinemedi!");
        }
      } catch (error) {
        alert("Bağlantı hatası!");
      }
    },
  },
};
</script>
