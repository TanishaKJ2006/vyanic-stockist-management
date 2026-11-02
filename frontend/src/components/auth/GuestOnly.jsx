import { Navigate } from "react-router";

import { useAuth } from "../../contexts/AuthContext.jsx";

export default function GuestOnly({ children }) {
  const { user, ready } = useAuth();

  if (!ready) {
    return (
      <main className="auth-restore" aria-live="polite">
        <span className="auth-restore-mark">V</span>
        <p>Verifying your secure session</p>
      </main>
    );
  }

  return user ? <Navigate to="/" replace /> : children;
}
