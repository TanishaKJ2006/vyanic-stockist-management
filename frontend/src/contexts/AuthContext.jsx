import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import apiClient from "../services/api/client.js";
import {
  clearSession,
  getSessionKey,
  readSessionState,
  saveSession,
} from "../services/auth/session.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);

  useEffect(() => {
    let active = true;
    const { session, expired } = readSessionState();

    if (!session) {
      if (expired) setSessionExpired(true);
      setReady(true);
      return () => {
        active = false;
      };
    }

    apiClient
      .get("/auth/me")
      .then(({ data }) => {
        if (!active) return;
        saveSession({ ...session, user: data });
        setUser(data);
      })
      .catch(() => {
        if (!active) return;
        clearSession();
        setUser(null);
      })
      .finally(() => {
        if (active) setReady(true);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const handleSessionExpired = () => {
      clearSession();
      setUser(null);
      setReady(true);
      setSessionExpired(true);
    };
    const handleStorage = (event) => {
      if (event.key === getSessionKey() && event.newValue === null) {
        setUser(null);
        setReady(true);
      }
    };

    window.addEventListener("auth:session-expired", handleSessionExpired);
    window.addEventListener("storage", handleStorage);
    return () => {
      window.removeEventListener("auth:session-expired", handleSessionExpired);
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  const login = useCallback(async (credentials) => {
    const { data } = await apiClient.post("/auth/login", credentials);
    const session = {
      accessToken: data.access_token,
      expiresAt: Date.now() + data.expires_in * 1000,
      user: data.user,
    };
    saveSession(session);
    setUser(data.user);
    setReady(true);
    setSessionExpired(false);
    return data.user;
  }, []);

  const register = useCallback(async (details) => {
    const { data } = await apiClient.post("/auth/register", details);
    return data;
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    setReady(true);
    setSessionExpired(false);
  }, []);

  const value = useMemo(
    () => ({ user, ready, sessionExpired, login, register, logout }),
    [user, ready, sessionExpired, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider.");
  return context;
}
