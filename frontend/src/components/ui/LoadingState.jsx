export default function LoadingState({ label = "Loading records" }) {
  return (
    <div className="state-panel state-panel--loading" role="status" aria-live="polite">
      <span className="loading-indicator" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
