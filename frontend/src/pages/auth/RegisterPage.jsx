import { useState } from "react";
import { Link, useNavigate } from "react-router";

import AuthLayout from "../../components/auth/AuthLayout.jsx";
import { useAuth } from "../../contexts/AuthContext.jsx";
import { getApiErrorMessage } from "../../services/api/errors.js";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirmation: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (form.password !== form.confirmation) {
      setError("The passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      await register({ name: form.name, email: form.email, password: form.password, role: "viewer" });
      navigate("/login", {
        replace: true,
        state: { message: "Your viewer account is ready. Sign in to continue." },
      });
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Your account could not be created."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout>
      <div className="auth-heading">
        <span className="auth-eyebrow">JOIN THE NETWORK</span>
        <h2>Create your account</h2>
        <p>Set up a read-only viewer account to access your Vyanic workspace.</p>
      </div>

      {error && <div className="auth-error" role="alert">{error}</div>}

      <form className="auth-form auth-form--register" onSubmit={handleSubmit}>
        <label className="auth-field">
          <span>Full name</span>
          <input
            type="text"
            name="name"
            autoComplete="name"
            placeholder="Your name"
            value={form.name}
            onChange={updateField}
            maxLength={150}
            required
          />
        </label>
        <label className="auth-field">
          <span>Email address</span>
          <input
            type="email"
            name="email"
            autoComplete="email"
            placeholder="you@company.com"
            value={form.email}
            onChange={updateField}
            maxLength={255}
            required
          />
        </label>
        <label className="auth-field">
          <span>Password <small>At least 12 characters</small></span>
          <input
            type="password"
            name="password"
            autoComplete="new-password"
            placeholder="Create a strong password"
            value={form.password}
            onChange={updateField}
            minLength={12}
            maxLength={128}
            required
          />
        </label>
        <label className="auth-field">
          <span>Confirm password</span>
          <input
            type="password"
            name="confirmation"
            autoComplete="new-password"
            placeholder="Enter your password again"
            value={form.confirmation}
            onChange={updateField}
            minLength={12}
            maxLength={128}
            required
          />
        </label>
        <button className="auth-submit" type="submit" disabled={submitting}>
          {submitting ? "Creating account..." : "Create viewer account"}
        </button>
      </form>

      <p className="auth-switch">
        Already registered? <Link to="/login">Sign in</Link>
      </p>
      <p className="auth-role-note">Administrator access is provisioned securely by the portal operator.</p>
    </AuthLayout>
  );
}
