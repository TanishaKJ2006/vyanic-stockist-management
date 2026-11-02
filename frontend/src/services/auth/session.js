const SESSION_KEY = "vyanic.auth.session";

export function readSessionState() {
  try {
    const session = JSON.parse(window.localStorage.getItem(SESSION_KEY) ?? "null");
    if (!session?.accessToken || !session?.expiresAt) {
      return { session: null, expired: false };
    }
    if (session.expiresAt <= Date.now()) {
      window.localStorage.removeItem(SESSION_KEY);
      return { session: null, expired: true };
    }
    return { session, expired: false };
  } catch {
    return { session: null, expired: false };
  }
}

export function getSession() {
  return readSessionState().session;
}

export function saveSession(session) {
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession() {
  try {
    window.localStorage.removeItem(SESSION_KEY);
  } catch {
    // The in-memory auth state is still cleared when storage is unavailable.
  }
}

export function getSessionKey() {
  return SESSION_KEY;
}
