import axios from "axios";

const API_URL = "http://127.0.0.1:3000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});
("");
export const loginUser = async (email, password) => {
  const response = await api.post("/auth/login", { email, password });
  return response.data;
};

export const sendMessage = async (token, message, chatId = null) => {
  const response = await api.post(
    "/chat/update-chat",
    { message, chatId },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
};
