import Icon from "./Icon.jsx";

export default function MetricCard({ label, description, icon, value, loading = false }) {
  return (
    <article className="metric-card">
      <div className="metric-card-top">
        <span className="metric-icon"><Icon name={icon} size={19} /></span>
        <span className="metric-period">TOTAL</span>
      </div>
      <div className="metric-label">{label}</div>
      <div className="metric-value" aria-label={loading ? `${label}: loading` : `${label}: ${value ?? "unavailable"}`}>
        {loading ? <span className="metric-skeleton" aria-hidden="true" /> : value ?? "—"}
      </div>
      <div className="metric-description">{description}</div>
    </article>
  );
}
