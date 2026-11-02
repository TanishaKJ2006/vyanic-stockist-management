import { useEffect, useMemo, useState } from "react";

import { AuditActionBadge, AuditDetail, formatTimestamp } from "../components/ui/ActivityList.jsx";
import EmptyState from "../components/ui/EmptyState.jsx";
import ErrorState from "../components/ui/ErrorState.jsx";
import LoadingState from "../components/ui/LoadingState.jsx";
import PageHeading from "../components/ui/PageHeading.jsx";
import apiClient from "../services/api/client.js";
import { getApiErrorMessage } from "../services/api/errors.js";

export default function AuditLogsPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");
    apiClient.get("/audit-logs", { signal: controller.signal })
      .then(({ data }) => setRecords(data))
      .catch((requestError) => {
        if (!controller.signal.aborted) setError(getApiErrorMessage(requestError, "Audit records are currently unavailable."));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [refreshKey]);

  const sortedRecords = useMemo(
    () => [...records]
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 50),
    [records],
  );

  return (
    <section className="page-section records-page">
      <PageHeading
        eyebrow="RECORD OF CHANGE"
        title="Audit logs"
        description="A transparent record of meaningful changes across the portal."
      >
        <span className="records-limit-label">LATEST 50 RECORDS</span>
      </PageHeading>

      <section className="content-card records-card audit-card">
        {error ? <div className="records-state"><ErrorState message={error} onRetry={() => setRefreshKey((current) => current + 1)} /></div> : null}
        {!error && loading ? <div className="records-state"><LoadingState label="Loading audit records" /></div> : null}
        {!error && !loading && sortedRecords.length === 0 ? (
          <div className="records-state"><EmptyState icon="audit" title="No activity recorded yet" description="Successful changes to portal records will be listed here." /></div>
        ) : null}
        {!error && !loading && sortedRecords.length > 0 ? (
          <div className="table-scroll">
            <table className="data-table audit-table">
              <thead><tr><th>Activity</th><th>Module</th><th>User</th><th>Details</th><th>Timestamp</th></tr></thead>
              <tbody>
                {sortedRecords.map((record) => (
                  <tr key={record.id}>
                    <td><AuditActionBadge action={record.action} /></td>
                    <td><span className="table-primary">{record.module}</span></td>
                    <td>{record.user_email}</td>
                    <td className="audit-details-cell"><AuditDetail details={record.details} /></td>
                    <td><time className="timestamp-cell" dateTime={record.timestamp}>{formatTimestamp(record.timestamp)}</time></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
        {!loading && !error && sortedRecords.length > 0 ? <div className="audit-count">Showing {sortedRecords.length} most recent {sortedRecords.length === 1 ? "entry" : "entries"}</div> : null}
      </section>
    </section>
  );
}
