// src/lib/axios.ts
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const api = axios.create({
    baseURL: API_BASE,
    timeout: 30000,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
});

// Attach token from localStorage/sessionStorage if present
api.interceptors.request.use((cfg) => {
    try {
        const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
        if (token) {
            cfg.headers = cfg.headers || {};
            cfg.headers["Authorization"] = `Bearer ${token}`;
        }
    } catch (e) {
        /* ignore */
    }
    return cfg;
});

// Do NOT clear token automatically on 401 - just surface error for debugging
api.interceptors.response.use(
    (res) => res,
    async (err) => {
        if (err?.response?.status === 401) {
            console.warn("API 401 received (frontend) — not clearing token automatically.");
            // Let UI handle showing login/notification
        }
        return Promise.reject(err);
    }
);

export default api;
