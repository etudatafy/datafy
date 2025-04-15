<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-12 col-md-10 col-lg-10">
        <!-- Orijinal renkli başlık bloğu -->
        <div class="row mb-4">
          <div class="col-12 text-center text-white bg-success py-4 px-4 rounded-3">
            <h1 class="fw-bold mb-2">Gelişim Analiz Sayfası</h1>
            <p class="mb-0">Sınav performansınızı grafiklerle analiz edin</p>
          </div>
        </div>

        <!-- TYT Grafikleri -->
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <div class="card shadow-sm border-success h-100">
              <div class="card-header bg-success text-white text-center">
                <span class="fw-bold">TYT Yığılmış Sütun Grafiği</span>
              </div>
              <div class="card-body">
                <div id="tytStackedChart"></div>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card shadow-sm border-success h-100">
              <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                <span class="fw-bold">TYT Çizgi Grafiği</span>
                <select
                  class="form-select form-select-sm w-50"
                  v-model="selectedTytLineSubject"
                  @change="updateTytLineChart"
                >
                  <option value="toplam">Toplam</option>
                  <option value="Türkçe">Türkçe</option>
                  <option value="Sosyal">Sosyal</option>
                  <option value="Matematik">Matematik</option>
                  <option value="Fen">Fen</option>
                </select>
              </div>
              <div class="card-body">
                <div id="tytLineChart"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- AYT Grafikleri -->
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <div class="card shadow-sm border-success h-100">
              <div class="card-header bg-success text-white text-center">
                <span class="fw-bold">AYT Yığılmış Sütun Grafiği</span>
              </div>
              <div class="card-body">
                <div id="aytStackedChart"></div>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card shadow-sm border-success h-100">
              <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                <span class="fw-bold">AYT Çizgi Grafiği</span>
                <select
                  class="form-select form-select-sm w-50"
                  v-model="selectedAytLineSubject"
                  @change="updateAytLineChart"
                >
                  <option value="toplam">Toplam</option>
                  <option value="Türkçe">Türkçe</option>
                  <option value="Sosyal">Sosyal</option>
                  <option value="Matematik">Matematik</option>
                  <option value="Fen">Fen</option>
                </select>
              </div>
              <div class="card-body">
                <div id="aytLineChart"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Birleşik Radar Grafiği -->
        <div class="row justify-content-center g-3 mb-3">
          <div class="col-12 col-md-8">
            <div class="card shadow-sm border-success">
              <div class="card-header bg-success text-white text-center">
                <span class="fw-bold">Birleşik Radar Grafiği</span>
              </div>
              <div class="card-body">
                <div id="combinedRadarChart"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Durum Mesajları -->
        <div v-if="loading" class="text-center my-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Yükleniyor...</span>
          </div>
          <p class="text-muted mt-2">Veriler yükleniyor...</p>
        </div>
        <div v-if="error" class="alert alert-danger text-center my-3">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApexCharts from "apexcharts"

export default {
  name: "ProgressAnalysis",
  data() {
    return {
      exams: [],
      loading: false,
      error: "",
      token: localStorage.getItem("jwt_token") || "",
      tytStackedChart: null,
      aytStackedChart: null,
      tytLineChart: null,
      aytLineChart: null,
      combinedRadarChart: null,
      selectedTytLineSubject: "toplam",
      selectedAytLineSubject: "toplam"
    }
  },
  methods: {
    async fetchProgress() {
      this.loading = true
      try {
        const res = await fetch("http://localhost:3000/api/progress/exam-details", {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        const body = await res.json()
        if (res.ok) {
          this.exams = Array.isArray(body) ? body : body.exams
          this.initTytStackedChart()
          this.initAytStackedChart()
          this.initTytLineChart()
          this.initAytLineChart()
          this.initCombinedRadarChart()
        } else {
          this.error = body.error || "Veri alınırken hata oluştu."
        }
      } catch (err) {
        this.error = "Bağlantı hatası!"
      } finally {
        this.loading = false
      }
    },
    getSortedExams() {
      return [...this.exams].sort((a, b) => new Date(a.date) - new Date(b.date))
    },
    initTytStackedChart() {
      if (this.tytStackedChart) this.tytStackedChart.destroy()
      const sorted = this.getSortedExams()
      const categories = []
      const turkceData = []
      const matematikData = []
      const sosyalData = []
      const fenData = []
      sorted.forEach(exam => {
        if (exam.results && exam.results.TYT) {
          const t = exam.results.TYT.turkce || 0
          const m = exam.results.TYT.matematik || 0
          const s = exam.results.TYT.sosyal || 0
          const f = exam.results.TYT.fen || 0
          if (t + m + s + f > 0) {
            categories.push(exam.name)
            turkceData.push(t)
            matematikData.push(m)
            sosyalData.push(s)
            fenData.push(f)
          }
        }
      })
      const options = {
        chart: { type: "bar", height: 250, stacked: true },
        plotOptions: { bar: { horizontal: false } },
        xaxis: { categories, labels: { style: { fontSize: "10px" } } },
        yaxis: { min: 0, max: 120 },
        series: [
          { name: "Türkçe", data: turkceData },
          { name: "Matematik", data: matematikData },
          { name: "Sosyal", data: sosyalData },
          { name: "Fen", data: fenData }
        ]
      }
      this.tytStackedChart = new ApexCharts(document.querySelector("#tytStackedChart"), options)
      this.tytStackedChart.render()
    },
    initAytStackedChart() {
      if (this.aytStackedChart) this.aytStackedChart.destroy()
      const sorted = this.getSortedExams()
      const categories = []
      const edebiyatData = []
      const matematikData = []
      const sosyalData = []
      const fenData = []
      sorted.forEach(exam => {
        if (exam.results && exam.results.AYT) {
          const t = exam.results.AYT.edebiyat || 0
          const m = exam.results.AYT.matematik_ayt || 0
          const s =
            (exam.results.AYT.tarih_1 || 0) +
            (exam.results.AYT.cografya_1 || 0) +
            (exam.results.AYT.tarih_2 || 0) +
            (exam.results.AYT.cografya_2 || 0) +
            (exam.results.AYT.felsefe || 0) +
            (exam.results.AYT.din || 0)
          const f =
            (exam.results.AYT.fizik || 0) +
            (exam.results.AYT.kimya || 0) +
            (exam.results.AYT.biyoloji || 0)
          if (t + m + s + f > 0) {
            categories.push(exam.name)
            edebiyatData.push(t)
            matematikData.push(m)
            sosyalData.push(s)
            fenData.push(f)
          }
        }
      })
      const options = {
        chart: { type: "bar", height: 250, stacked: true },
        plotOptions: { bar: { horizontal: false } },
        xaxis: { categories, labels: { style: { fontSize: "10px" } } },
        yaxis: { min: 0, max: 160 },
        series: [
          { name: "Türkçe", data: edebiyatData },
          { name: "Matematik", data: matematikData },
          { name: "Sosyal", data: sosyalData },
          { name: "Fen", data: fenData }
        ]
      }
      this.aytStackedChart = new ApexCharts(document.querySelector("#aytStackedChart"), options)
      this.aytStackedChart.render()
    },
    initTytLineChart() {
      if (this.tytLineChart) this.tytLineChart.destroy()
      const options = this.getTytLineChartOptions(this.selectedTytLineSubject)
      this.tytLineChart = new ApexCharts(document.querySelector("#tytLineChart"), options)
      this.tytLineChart.render()
    },
    getTytLineChartOptions(subjectOption) {
      const sorted = this.getSortedExams()
      const categories = []
      const data = []
      if (subjectOption === "toplam") {
        sorted.forEach(exam => {
          if (exam.results && exam.results.TYT) {
            const t = exam.results.TYT.turkce || 0
            const m = exam.results.TYT.matematik || 0
            const s = exam.results.TYT.sosyal || 0
            const f = exam.results.TYT.fen || 0
            const total = t + m + s + f
            if (total > 0) {
              categories.push(exam.name)
              data.push(total)
            }
          }
        })
      } else {
        const field =
          subjectOption === "Türkçe"
            ? "turkce"
            : subjectOption === "Matematik"
            ? "matematik"
            : subjectOption === "Sosyal"
            ? "sosyal"
            : "fen"
        sorted.forEach(exam => {
          if (exam.results && exam.results.TYT) {
            const val = exam.results.TYT[field] || 0
            if (val > 0) {
              categories.push(exam.name)
              data.push(val)
            }
          }
        })
      }
      let maxY =
        subjectOption === "toplam"
          ? 120
          : subjectOption === "Sosyal" || subjectOption === "Fen"
          ? 20
          : 40
      return {
        chart: { type: "line", height: 250 },
        xaxis: { categories, labels: { style: { fontSize: "10px" } } },
        yaxis: { min: 0, max: maxY },
        series: [{ name: subjectOption, data }]
      }
    },
    updateTytLineChart() {
      if (this.tytLineChart) {
        this.tytLineChart.updateOptions(this.getTytLineChartOptions(this.selectedTytLineSubject))
      }
    },
    initAytLineChart() {
      if (this.aytLineChart) this.aytLineChart.destroy()
      const options = this.getAytLineChartOptions(this.selectedAytLineSubject)
      this.aytLineChart = new ApexCharts(document.querySelector("#aytLineChart"), options)
      this.aytLineChart.render()
    },
    getAytLineChartOptions(subjectOption) {
      const sorted = this.getSortedExams()
      const categories = []
      const data = []
      if (subjectOption === "toplam") {
        sorted.forEach(exam => {
          if (exam.results && exam.results.AYT) {
            const t = exam.results.AYT.edebiyat || 0
            const m = exam.results.AYT.matematik_ayt || 0
            const s =
              (exam.results.AYT.tarih_1 || 0) +
              (exam.results.AYT.cografya_1 || 0) +
              (exam.results.AYT.tarih_2 || 0) +
              (exam.results.AYT.cografya_2 || 0) +
              (exam.results.AYT.felsefe || 0) +
              (exam.results.AYT.din || 0)
            const f =
              (exam.results.AYT.fizik || 0) +
              (exam.results.AYT.kimya || 0) +
              (exam.results.AYT.biyoloji || 0)
            const total = t + m + s + f
            if (total > 0) {
              categories.push(exam.name)
              data.push(total)
            }
          }
        })
      } else {
        if (subjectOption === "Türkçe") {
          sorted.forEach(exam => {
            if (exam.results && exam.results.AYT) {
              const val = exam.results.AYT.edebiyat || 0
              if (val > 0) {
                categories.push(exam.name)
                data.push(val)
              }
            }
          })
        } else if (subjectOption === "Matematik") {
          sorted.forEach(exam => {
            if (exam.results && exam.results.AYT) {
              const val = exam.results.AYT.matematik_ayt || 0
              if (val > 0) {
                categories.push(exam.name)
                data.push(val)
              }
            }
          })
        } else if (subjectOption === "Sosyal") {
          sorted.forEach(exam => {
            if (exam.results && exam.results.AYT) {
              const val =
                (exam.results.AYT.tarih_1 || 0) +
                (exam.results.AYT.cografya_1 || 0) +
                (exam.results.AYT.tarih_2 || 0) +
                (exam.results.AYT.cografya_2 || 0) +
                (exam.results.AYT.felsefe || 0) +
                (exam.results.AYT.din || 0)
              if (val > 0) {
                categories.push(exam.name)
                data.push(val)
              }
            }
          })
        } else if (subjectOption === "Fen") {
          sorted.forEach(exam => {
            if (exam.results && exam.results.AYT) {
              const val =
                (exam.results.AYT.fizik || 0) +
                (exam.results.AYT.kimya || 0) +
                (exam.results.AYT.biyoloji || 0)
              if (val > 0) {
                categories.push(exam.name)
                data.push(val)
              }
            }
          })
        }
      }
      let maxY = subjectOption === "toplam" ? 160 : 40
      return {
        chart: { type: "line", height: 250 },
        xaxis: { categories, labels: { style: { fontSize: "10px" } } },
        yaxis: { min: 0, max: maxY },
        series: [{ name: subjectOption, data }]
      }
    },
    updateAytLineChart() {
      if (this.aytLineChart) {
        this.aytLineChart.updateOptions(this.getAytLineChartOptions(this.selectedAytLineSubject))
      }
    },
    initCombinedRadarChart() {
      if (this.combinedRadarChart) this.combinedRadarChart.destroy()
      const categories = ["Türkçe", "Matematik", "Sosyal", "Fen"]
      const tytAverages = this.getOverallAverage("TYT", [
        "turkce",
        "matematik",
        "sosyal",
        "fen"
      ])
      const aytAverages = this.getOverallAverage("AYT", [
        "edebiyat",
        "matematik_ayt",
        "sosyal",
        "fen"
      ])
      const options = {
        chart: { type: "radar", height: 250 },
        series: [
          { name: "TYT", data: tytAverages },
          { name: "AYT", data: aytAverages }
        ],
        labels: categories,
        yaxis: { show: true, min: 0 }
      }
      this.combinedRadarChart = new ApexCharts(document.querySelector("#combinedRadarChart"), options)
      this.combinedRadarChart.render()
    },
    getOverallAverage(examType, fields) {
      let sums = {}
      fields.forEach(f => (sums[f] = 0))
      let count = 0
      this.exams.forEach(exam => {
        if (exam.results && exam.results[examType]) {
          count++
          if (examType === "TYT") {
            fields.forEach(f => {
              sums[f] += exam.results.TYT[f] || 0
            })
          } else {
            fields.forEach(f => {
              if (f === "sosyal") {
                const social =
                  (exam.results.AYT.tarih_1 || 0) +
                  (exam.results.AYT.cografya_1 || 0) +
                  (exam.results.AYT.tarih_2 || 0) +
                  (exam.results.AYT.cografya_2 || 0) +
                  (exam.results.AYT.felsefe || 0) +
                  (exam.results.AYT.din || 0)
                sums[f] += social
              } else if (f === "fen") {
                const fen =
                  (exam.results.AYT.fizik || 0) +
                  (exam.results.AYT.kimya || 0) +
                  (exam.results.AYT.biyoloji || 0)
                sums[f] += fen
              } else {
                sums[f] += exam.results.AYT[f] || 0
              }
            })
          }
        }
      })
      return fields.map(f => (count ? parseFloat((sums[f] / count).toFixed(2)) : 0))
    }
  },
  mounted() {
    this.fetchProgress()
  }
}
</script>