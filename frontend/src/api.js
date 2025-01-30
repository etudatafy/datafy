import axios from "axios";

// Axios örneği oluştur
const api = axios.create({
  baseURL: "http://localhost:5000", // Backend API'nin base URL'i
  timeout: 5000, // Zaman aşımı süresi
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
