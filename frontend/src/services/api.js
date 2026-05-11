import axios from "axios";

const BASE = "http://localhost:8000";

const api = axios.create({ baseURL: BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authAPI = {
  register: (email, password) =>
    api.post("/auth/register", { email, password }),
  login: (email, password) => api.post("/auth/login", { email, password }),
  verify2fa: (temp_token, code) =>
    api.post("/auth/verify-2fa", { temp_token, code }),
};

export const scanAPI = {
  scan: (url) => api.post("/scan", { url }),
  history: () => api.get("/scan/history"),
};

export const adminAPI = {
  scans: () => api.get("/admin/scans"),
  users: () => api.get("/admin/users"),
};
