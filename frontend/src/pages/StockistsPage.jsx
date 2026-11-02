import { useEffect, useState } from "react";

import AccessNotice from "../components/ui/AccessNotice.jsx";
import EmptyState from "../components/ui/EmptyState.jsx";
import ErrorState from "../components/ui/ErrorState.jsx";
import Icon from "../components/ui/Icon.jsx";
import LoadingState from "../components/ui/LoadingState.jsx";
import Modal from "../components/ui/Modal.jsx";
import PageHeading from "../components/ui/PageHeading.jsx";
import { formatTimestamp } from "../components/ui/ActivityList.jsx";
import { useAuth } from "../contexts/AuthContext.jsx";
import apiClient from "../services/api/client.js";
import { getApiErrorMessage } from "../services/api/errors.js";

function StockistForm({ onSave, onCancel }) {
  const [form, setForm] = useState({ name: "", contact_email: "", contact_phone: "", city: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function update(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      await onSave(form);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "The stockist could not be created."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="record-form" onSubmit={submit}>
      {error ? <div className="form-message form-message--error" role="alert">{error}</div> : null}
      <div className="form-grid">
        <label className="form-field form-field--wide"><span>Stockist name</span><input name="name" value={form.name} onChange={update} maxLength={180} required autoFocus /></label>
        <label className="form-field form-field--wide"><span>Contact email</span><input name="contact_email" type="email" value={form.contact_email} onChange={update} maxLength={255} required /></label>
        <label className="form-field"><span>Contact phone</span><input name="contact_phone" type="tel" value={form.contact_phone} onChange={update} minLength={7} maxLength={32} required /></label>
        <label className="form-field"><span>City</span><input name="city" value={form.city} onChange={update} maxLength={120} required /></label>
      </div>
      <div className="form-actions">
        <button className="button button--quiet" type="button" onClick={onCancel} disabled={saving}>Cancel</button>
        <button className="button button--primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Create stockist"}</button>
      </div>
    </form>
  );
}

function PincodeForm({ stockist, onAssign, onCancel }) {
  const [form, setForm] = useState({ pincode: "", state: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      await onAssign(form);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "The pincode could not be assigned."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="record-form" onSubmit={submit}>
      <div className="assignment-target"><span>ASSIGNING TO</span><strong>{stockist.name}</strong><small>{stockist.city}</small></div>
      {error ? <div className="form-message form-message--error" role="alert">{error}</div> : null}
      <div className="form-grid">
        <label className="form-field"><span>Six-digit pincode</span><input name="pincode" inputMode="numeric" autoComplete="postal-code" pattern="[0-9]{6}" minLength={6} maxLength={6} placeholder="110001" value={form.pincode} onChange={(event) => setForm((current) => ({ ...current, pincode: event.target.value.replace(/\D/g, "").slice(0, 6) }))} required autoFocus /></label>
        <label className="form-field"><span>State</span><input name="state" value={form.state} onChange={(event) => setForm((current) => ({ ...current, state: event.target.value }))} maxLength={120} required /></label>
      </div>
      <div className="form-actions">
        <button className="button button--quiet" type="button" onClick={onCancel} disabled={saving}>Cancel</button>
        <button className="button button--primary" type="submit" disabled={saving}>{saving ? "Assigning…" : "Assign pincode"}</button>
      </div>
    </form>
  );
}

export default function StockistsPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [stockists, setStockists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);
  const [creating, setCreating] = useState(false);
  const [assigningTo, setAssigningTo] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [pincodeData, setPincodeData] = useState({});

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");
    apiClient.get("/stockists", { signal: controller.signal })
      .then(({ data }) => setStockists(data))
      .catch((requestError) => {
        if (!controller.signal.aborted) setError(getApiErrorMessage(requestError, "Stockists are currently unavailable."));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [refreshKey]);

  useEffect(() => {
    if (expandedId === null) return undefined;
    const current = pincodeData[expandedId];
    if (current?.loaded || current?.loading) return undefined;
    const controller = new AbortController();
    setPincodeData((state) => ({ ...state, [expandedId]: { items: [], loading: true, error: "", loaded: false } }));
    apiClient.get(`/stockists/${expandedId}/pincodes`, { signal: controller.signal })
      .then(({ data }) => setPincodeData((state) => ({ ...state, [expandedId]: { items: data, loading: false, error: "", loaded: true } })))
      .catch((requestError) => {
        if (!controller.signal.aborted) setPincodeData((state) => ({ ...state, [expandedId]: { items: [], loading: false, error: getApiErrorMessage(requestError, "Pincodes could not be loaded."), loaded: false } }));
      });
    return () => controller.abort();
  }, [expandedId]);

  async function createStockist(payload) {
    await apiClient.post("/stockists", payload);
    setCreating(false);
    setRefreshKey((current) => current + 1);
  }

  async function assignPincode(payload) {
    const stockistId = assigningTo.id;
    await apiClient.post(`/stockists/${stockistId}/pincodes`, payload);
    try {
      const { data } = await apiClient.get(`/stockists/${stockistId}/pincodes`);
      setPincodeData((state) => ({ ...state, [stockistId]: { items: data, loading: false, error: "", loaded: true } }));
    } catch {
      setPincodeData((state) => ({ ...state, [stockistId]: { ...state[stockistId], loading: false, loaded: true, error: "The pincode was assigned, but the updated list could not be refreshed. Please close and reopen this list to retry." } }));
    }
    setExpandedId(stockistId);
    setAssigningTo(null);
  }

  function togglePincodes(stockistId) {
    setExpandedId((current) => current === stockistId ? null : stockistId);
    if (pincodeData[stockistId]?.error) {
      setPincodeData((state) => ({ ...state, [stockistId]: { ...state[stockistId], loaded: false, error: "" } }));
    }
  }

  return (
    <section className="page-section records-page">
      <PageHeading
        eyebrow="PARTNER NETWORK"
        title="Stockists"
        description="Review stockist contacts and the service locations assigned to each partner."
      >
        {isAdmin ? <button className="button button--primary" type="button" onClick={() => setCreating(true)}><Icon name="plus" size={17} /> Add stockist</button> : null}
      </PageHeading>

      {!isAdmin ? <AccessNotice /> : null}
      {error ? <ErrorState message={error} onRetry={() => setRefreshKey((current) => current + 1)} /> : null}
      {!error && loading ? <section className="content-card records-card records-state"><LoadingState label="Loading stockists" /></section> : null}
      {!error && !loading && stockists.length === 0 ? (
        <section className="content-card records-state"><EmptyState icon="stockists" title="No stockists yet" description={isAdmin ? "Add a stockist to begin building the partner network." : "Stockist records will appear here when they are added."} /></section>
      ) : null}

      {!error && !loading && stockists.length > 0 ? (
        <div className="stockist-grid">
          {stockists.map((stockist) => {
            const assigned = pincodeData[stockist.id];
            const expanded = expandedId === stockist.id;
            return (
              <article className={`content-card stockist-card${expanded ? " stockist-card--expanded" : ""}`} key={stockist.id}>
                <header className="stockist-card-header">
                  <div className="stockist-avatar" aria-hidden="true">{stockist.name.trim().charAt(0).toUpperCase()}</div>
                  <div className="stockist-card-title"><h2>{stockist.name}</h2><span>{stockist.city}</span></div>
                  {isAdmin ? <button className="button button--outline button--small" type="button" onClick={() => setAssigningTo(stockist)}><Icon name="plus" size={15} /> Assign pincode</button> : null}
                </header>
                <div className="stockist-contact-grid">
                  <div><span>EMAIL</span><a href={`mailto:${stockist.contact_email}`}>{stockist.contact_email}</a></div>
                  <div><span>PHONE</span><a href={`tel:${stockist.contact_phone.replace(/[^+\d]/g, "")}`}>{stockist.contact_phone}</a></div>
                </div>
                <button className="pincode-toggle" type="button" onClick={() => togglePincodes(stockist.id)} aria-expanded={expanded}>
                  <span><strong>Service pincodes</strong>{assigned?.loaded ? <small>{assigned.items.length} assigned</small> : null}</span>
                  <Icon name="chevron" size={18} className={expanded ? "chevron-rotated" : ""} />
                </button>
                {expanded ? (
                  <div className="pincode-panel">
                    {assigned?.loading ? <LoadingState label="Loading assigned pincodes" /> : null}
                    {assigned?.error ? <div className="form-message form-message--error" role="alert">{assigned.error}</div> : null}
                    {!assigned?.loading && !assigned?.error && assigned?.loaded && !assigned.items.length ? <p className="pincode-empty">No pincodes assigned to this stockist.</p> : null}
                    {!assigned?.loading && !assigned?.error && assigned?.items?.length ? (
                      <ul className="pincode-list">
                        {assigned.items.map((pincode) => (
                          <li key={pincode.id}><span className="pincode-code">{pincode.pincode}</span><span>{pincode.state}</span><time dateTime={pincode.created_at}>{formatTimestamp(pincode.created_at, false)}</time></li>
                        ))}
                      </ul>
                    ) : null}
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      ) : null}

      {creating ? <Modal title="Add a stockist" description="Create a stockist profile for the partner network." onClose={() => setCreating(false)}><StockistForm onSave={createStockist} onCancel={() => setCreating(false)} /></Modal> : null}
      {assigningTo ? <Modal title="Assign a service pincode" description="Pincodes can belong to one stockist only." onClose={() => setAssigningTo(null)}><PincodeForm stockist={assigningTo} onAssign={assignPincode} onCancel={() => setAssigningTo(null)} /></Modal> : null}
    </section>
  );
}
