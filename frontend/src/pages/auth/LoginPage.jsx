import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";

import AuthLayout from "../../components/auth/AuthLayout.jsx";
import Icon from "../../components/ui/Icon.jsx";
import { useAuth } from "../../contexts/AuthContext.jsx";
import { getApiErrorMessage } from "../../services/api/errors.js";

export default function LoginPage() {
  const { login } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const successMessage = location.state?.message;
  const expired = location.state?.expired;

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login({ email, password });
      const destination = location.state?.from?.pathname || "/";
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "The email or password could not be verified."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout>
      <div className="auth-heading">
        <span className="auth-eyebrow">WELCOME BACK</span>
        <h2>Sign in to your workspace</h2>
        <p>Enter your account details to continue to Vyanic operations.</p>
      </div>

      {expired && (
        <div className="auth-notice" role="status">
          Your session expired. Sign in again to continue.
        </div>
      )}
      {successMessage && (
        <div className="auth-success" role="status">{successMessage}</div>
      )}
      {error && <div className="auth-error" role="alert">{error}</div>}

      <form className="auth-form" onSubmit={handleSubmit}>
        <label className="auth-field">
          <span>Email address</span>
          <input
            type="email"
            name="email"
            autoComplete="email"
            placeholder="you@company.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            maxLength={255}
            required
          />
        </label>
        <label className="auth-field">
          <span>Password</span>
          <input
            type="password"
            name="password"
            autoComplete="current-password"
            placeholder="Enter your password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            maxLength={128}
            required
          />
        </label>
        <button className="auth-submit" type="submit" disabled={submitting}>
          {submitting ? "Signing in..." : "Sign in"}
          {!submitting && <Icon name="arrow" size={17} />}
        </button>
      </form>

      <p className="auth-switch">
        New to the portal? <Link to="/register">Create a viewer account</Link>
      </p>
    </AuthLayout>
  );
}
