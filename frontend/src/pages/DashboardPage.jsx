import { useEffect, useState } from "react";

import AccessNotice from "../components/ui/AccessNotice.jsx";
import { ActivityList } from "../components/ui/ActivityList.jsx";
import ErrorState from "../components/ui/ErrorState.jsx";
import Icon from "../components/ui/Icon.jsx";
import LoadingState from "../components/ui/LoadingState.jsx";
import MetricCard from "../components/ui/MetricCard.jsx";
import PageHeading from "../components/ui/PageHeading.jsx";
import { useAuth } from "../contexts/AuthContext.jsx";
import apiClient from "../services/api/client.js";
import { getApiErrorMessage } from "../services/api/errors.js";

const metrics = [
  { label: "Products", key: "total_products", description: "Items in your catalog", icon: "products" },
  { label: "Stockists", key: "total_stockists", description: "Partners in your network", icon: "stockists" },
  { label: "Pincodes", key: "total_pincodes_assigned", description: "Assigned service locations", icon: "dashboard" },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");
    setStats(null);
    apiClient.get("/dashboard/stats", { signal: controller.signal })
      .then(({ data }) => setStats(data))
      .catch((requestError) => {
        if (!controller.signal.aborted) {
          setError(getApiErrorMessage(requestError, "Dashboard data is currently unavailable."));
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [refreshKey]);

  return (
    <section className="page-section dashboard-page">
      <PageHeading
        eyebrow="VYANIC OPERATIONS"
        title="Welcome to your workspace"
        description="A considered overview of products, stockists, and the locations they serve."
      />

      {error ? <ErrorState message={error} onRetry={() => setRefreshKey((current) => current + 1)} /> : null}

      <div className="metric-grid">
        {metrics.map((metric) => (
          <MetricCard
            key={metric.key}
            {...metric}
            value={stats?.[metric.key]}
            loading={loading && !stats}
          />
        ))}
      </div>

      <div className="dashboard-lower-grid">
        <section className="content-card activity-card">
          <div className="card-heading-row">
            <div>
              <div className="card-eyebrow">ACTIVITY</div>
              <h2>Recent activity</h2>
            </div>
            <span className="activity-heading-icon"><Icon name="activity" size={19} /></span>
          </div>
          {loading && !stats
            ? <LoadingState label="Loading recent activity" />
            : <ActivityList entries={stats?.recent_activity ?? []} compact />}
        </section>

        <section className="content-card access-card">
          <div className="connection-card-heading">
            <span className="connection-icon"><Icon name="shield" size={19} /></span>
            <span className="connection-label">WORKSPACE ACCESS</span>
          </div>
          <div className="access-card-role">
            {user?.role === "admin" ? "Administrator" : user?.role === "stockist" ? "Stockist · read only" : "Viewer · read only"}
          </div>
          <p>{user?.role === "admin"
            ? "You can manage catalog records, stockist profiles and pincode coverage."
            : "You can review current records and activity across the stockist portal."}</p>
          {user?.role !== "admin" ? <AccessNotice /> : null}
        </section>
      </div>
    </section>
  );
}
