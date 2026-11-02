import EmptyState from "./EmptyState.jsx";

export function formatTimestamp(value, includeTime = true) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value ?? "—");
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    ...(includeTime ? { timeStyle: "short" } : {}),
  }).format(date);
}

export function AuditActionBadge({ action }) {
  const normalized = String(action ?? "").toUpperCase();
  const className = {
    CREATE: "audit-badge--create",
    UPDATE: "audit-badge--update",
    DELETE: "audit-badge--delete",
  }[normalized] ?? "audit-badge--neutral";
  return <span className={`audit-badge ${className}`}>{normalized || "UNKNOWN"}</span>;
}

function describeDetails(details) {
  if (!details || typeof details !== "object" || Object.keys(details).length === 0) return "No additional details";
  return Object.entries(details)
    .map(([key, value]) => {
      const label = key.replaceAll("_", " ");
      const displayValue = value && typeof value === "object" ? JSON.stringify(value) : String(value);
      return `${label}: ${displayValue}`;
    })
    .join(" · ");
}

export function AuditDetail({ details }) {
  const summary = describeDetails(details);
  return <span className="audit-detail" title={summary}>{summary}</span>;
}

export function ActivityList({ entries, compact = false }) {
  if (!entries?.length) {
    return (
      <EmptyState
        icon="audit"
        title="No activity recorded yet"
        description="New changes will appear here after they are recorded by the portal."
      />
    );
  }

  return (
    <ol className={`activity-list${compact ? " activity-list--compact" : ""}`}>
      {entries.map((entry) => (
        <li className="activity-entry" key={entry.id}>
          <span className="activity-entry-marker" aria-hidden="true" />
          <div className="activity-entry-main">
            <div className="activity-entry-title">
              <AuditActionBadge action={entry.action} />
              <span>{entry.module}</span>
            </div>
            <AuditDetail details={entry.details} />
            <div className="activity-entry-meta">
              <span>{entry.user_email}</span>
              <time dateTime={entry.timestamp}>{formatTimestamp(entry.timestamp)}</time>
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
}
