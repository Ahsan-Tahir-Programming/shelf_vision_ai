// frontend/src/api.js
import axios from "axios";

const BASE_URL = "http://localhost:8000/api";

const api = axios.create({ baseURL: BASE_URL });

// Upload image and analyze shelf
export const analyzeShelf = async (file, storeName, notes = "") => {
  const formData = new FormData();
  formData.append("image", file);
  formData.append("store_name", storeName);
  formData.append("notes", notes);
  const res = await api.post("/analyze", formData);
  return res.data;
};

// Send chat message to agent
export const sendChatMessage = async (storeName, message) => {
  const formData = new FormData();
  formData.append("store_name", storeName);
  formData.append("message", message);
  const res = await api.post("/chat", formData);
  return res.data;
};

// Get audit history
export const getHistory = async (storeName) => {
  const res = await api.get(`/history/${encodeURIComponent(storeName)}`);
  return res.data;
};

// Get database stats
export const getStats = async () => {
  const res = await api.get("/stats");
  return res.data;
};
