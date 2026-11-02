import axios from "axios";

import { clearSession, getSession } from "../auth/session.js";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 10_000,
  headers: {
    Accept: "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const session = getSession();
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const path = error.config?.url ?? "";
    const isCredentialSubmission = path.startsWith("/auth/login") || path.startsWith("/auth/register");

    if (error.response?.status === 401 && !isCredentialSubmission) {
      clearSession();
      window.dispatchEvent(new CustomEvent("auth:session-expired"));
    }

    return Promise.reject(error);
  },
);

export default apiClient;
