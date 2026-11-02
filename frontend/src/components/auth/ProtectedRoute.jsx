import { Navigate, useLocation } from "react-router";

import { useAuth } from "../../contexts/AuthContext.jsx";

export default function ProtectedRoute({ children }) {
  const { user, ready, sessionExpired } = useAuth();
  const location = useLocation();

  if (!ready) {
    return (
      <main className="auth-restore" aria-live="polite">
        <span className="auth-restore-mark">V</span>
        <p>Verifying your secure session</p>
      </main>
    );
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location, expired: sessionExpired }}
      />
    );
  }

  return children;
}
