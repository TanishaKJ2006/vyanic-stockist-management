import { useEffect, useMemo, useState } from "react";

import AccessNotice from "../components/ui/AccessNotice.jsx";
import EmptyState from "../components/ui/EmptyState.jsx";
import ErrorState from "../components/ui/ErrorState.jsx";
import Icon from "../components/ui/Icon.jsx";
import LoadingState from "../components/ui/LoadingState.jsx";
import Modal from "../components/ui/Modal.jsx";
import PageHeading from "../components/ui/PageHeading.jsx";
import { useAuth } from "../contexts/AuthContext.jsx";
import apiClient from "../services/api/client.js";
import { getApiErrorMessage } from "../services/api/errors.js";

const PAGE_SIZE = 10;
const currency = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 });

function ProductForm({ product, onSave, onCancel }) {
  const [form, setForm] = useState({
    name: product?.name ?? "",
    sku_code: product?.sku_code ?? "",
    category: product?.category ?? "",
    price: product?.price ?? "",
    stock_quantity: product?.stock_quantity ?? "0",
  });
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
      await onSave({
        ...form,
        price: Number(form.price),
        stock_quantity: Number(form.stock_quantity),
      });
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "The product could not be saved."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="record-form" onSubmit={submit}>
      {error ? <div className="form-message form-message--error" role="alert">{error}</div> : null}
      <div className="form-grid">
        <label className="form-field form-field--wide">
          <span>Product name</span>
          <input name="name" value={form.name} onChange={update} maxLength={180} required autoFocus />
        </label>
        <label className="form-field">
          <span>SKU</span>
          <input name="sku_code" value={form.sku_code} onChange={update} maxLength={64} required />
        </label>
        <label className="form-field">
          <span>Category</span>
          <input name="category" value={form.category} onChange={update} maxLength={120} required />
        </label>
        <label className="form-field">
          <span>Price (INR)</span>
          <input name="price" type="number" min="0" step="0.01" value={form.price} onChange={update} required />
        </label>
        <label className="form-field">
          <span>Stock quantity</span>
          <input name="stock_quantity" type="number" min="0" step="1" value={form.stock_quantity} onChange={update} required />
        </label>
      </div>
      <div className="form-actions">
        <button className="button button--quiet" type="button" onClick={onCancel} disabled={saving}>Cancel</button>
        <button className="button button--primary" type="submit" disabled={saving}>
          {saving ? "Saving…" : product ? "Save changes" : "Create product"}
        </button>
      </div>
    </form>
  );
}

export default function ProductsPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [categoryInput, setCategoryInput] = useState("");
  const [filters, setFilters] = useState({ search: "", category: "" });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);
  const [editing, setEditing] = useState(null);
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [deleteError, setDeleteError] = useState("");
  const [deleteBusy, setDeleteBusy] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");
    apiClient.get("/products", {
      params: { page, limit: PAGE_SIZE, search: filters.search || undefined, category: filters.category || undefined },
      signal: controller.signal,
    })
      .then(({ data }) => setResult(data))
      .catch((requestError) => {
        if (!controller.signal.aborted) setError(getApiErrorMessage(requestError, "Products are currently unavailable."));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [page, filters, refreshKey]);

  const categories = useMemo(
    () => [...new Set((result?.items ?? []).map((item) => item.category))].sort((a, b) => a.localeCompare(b)),
    [result],
  );

  function applyFilters(event) {
    event.preventDefault();
    setPage(1);
    setFilters({ search: searchInput.trim(), category: categoryInput.trim() });
  }

  async function saveProduct(payload) {
    if (editing) await apiClient.put(`/products/${editing.id}`, payload);
    else await apiClient.post("/products", payload);
    setCreating(false);
    setEditing(null);
    setRefreshKey((current) => current + 1);
  }

  async function confirmDelete() {
    if (!deleting) return;
    setDeleteBusy(true);
    setDeleteError("");
    try {
      await apiClient.delete(`/products/${deleting.id}`);
      setDeleting(null);
      if (rows.length === 1 && page > 1) setPage((current) => current - 1);
      else setRefreshKey((current) => current + 1);
    } catch (requestError) {
      setDeleteError(getApiErrorMessage(requestError, "The product could not be deleted."));
    } finally {
      setDeleteBusy(false);
    }
  }

  const rows = result?.items ?? [];
  const pageCount = Math.max(1, result?.pages ?? 1);

  return (
    <section className="page-section records-page">
      <PageHeading
        eyebrow="CATALOG"
        title="Products"
        description="Maintain a clear, current view of products available across your stockist network."
      >
        {isAdmin ? (
          <button className="button button--primary" type="button" onClick={() => setCreating(true)}>
            <Icon name="plus" size={17} /> Add product
          </button>
        ) : null}
      </PageHeading>

      {!isAdmin ? <AccessNotice /> : null}

      <section className="content-card records-card">
        <form className="filter-bar" onSubmit={applyFilters}>
          <label className="filter-field filter-field--search">
            <span className="visually-hidden">Search products</span>
            <Icon name="search" size={17} />
            <input
              type="search"
              placeholder="Search name or SKU"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
            />
          </label>
          <label className="filter-field filter-field--category">
            <span className="visually-hidden">Filter by category</span>
            <input
              list="product-categories"
              placeholder="All categories"
              value={categoryInput}
              onChange={(event) => setCategoryInput(event.target.value)}
            />
            <datalist id="product-categories">
              {categories.map((category) => <option key={category} value={category} />)}
            </datalist>
          </label>
          <button className="button button--secondary" type="submit">Apply filters</button>
          {(filters.search || filters.category) ? (
            <button className="text-button filter-clear" type="button" onClick={() => {
              setSearchInput(""); setCategoryInput(""); setFilters({ search: "", category: "" }); setPage(1);
            }}>Clear</button>
          ) : null}
          <span className="record-count">{result ? `${result.total} ${result.total === 1 ? "record" : "records"}` : ""}</span>
        </form>

        {error ? <div className="records-state"><ErrorState message={error} onRetry={() => setRefreshKey((current) => current + 1)} /></div> : null}
        {!error && loading ? <div className="records-state"><LoadingState label="Loading products" /></div> : null}
        {!error && !loading && !rows.length ? (
          <div className="records-state">
            <EmptyState
              icon="products"
              title={filters.search || filters.category ? "No matching products" : "No products yet"}
              description={filters.search || filters.category
                ? "Adjust your search or category filter and try again."
                : isAdmin ? "Add the first product to start building the catalog." : "Product records will appear here when they are added."}
            />
          </div>
        ) : null}
        {!error && !loading && rows.length ? (
          <>
            <div className="table-scroll">
              <table className="data-table">
                <thead><tr><th>Product</th><th>SKU</th><th>Category</th><th className="numeric-cell">Price</th><th className="numeric-cell">Stock</th>{isAdmin ? <th><span className="visually-hidden">Actions</span></th> : null}</tr></thead>
                <tbody>
                  {rows.map((product) => (
                    <tr key={product.id}>
                      <td><span className="table-primary">{product.name}</span></td>
                      <td><span className="sku-label">{product.sku_code}</span></td>
                      <td>{product.category}</td>
                      <td className="numeric-cell">{currency.format(Number(product.price))}</td>
                      <td className="numeric-cell"><span className={`stock-value${product.stock_quantity === 0 ? " stock-value--empty" : ""}`}>{product.stock_quantity.toLocaleString("en-IN")}</span></td>
                      {isAdmin ? (
                        <td>
                          <div className="row-actions">
                            <button className="icon-button row-action" type="button" aria-label={`Edit ${product.name}`} title="Edit product" onClick={() => setEditing(product)}><Icon name="edit" size={16} /></button>
                            <button className="icon-button row-action row-action--danger" type="button" aria-label={`Delete ${product.name}`} title="Delete product" onClick={() => { setDeleteError(""); setDeleting(product); }}><Icon name="trash" size={16} /></button>
                          </div>
                        </td>
                      ) : null}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pagination-bar">
              <span>Page {page} of {pageCount}</span>
              <div className="pagination-actions">
                <button className="button button--quiet" type="button" disabled={page <= 1 || loading} onClick={() => setPage((current) => current - 1)}>Previous</button>
                <button className="button button--quiet" type="button" disabled={page >= pageCount || loading} onClick={() => setPage((current) => current + 1)}>Next</button>
              </div>
            </div>
          </>
        ) : null}
      </section>

      {creating || editing ? (
        <Modal
          title={editing ? "Edit product" : "Add a product"}
          description={editing ? "Update the catalog details for this product." : "Enter the catalog details to add a product."}
          onClose={() => { setCreating(false); setEditing(null); }}
        >
          <ProductForm product={editing} onSave={saveProduct} onCancel={() => { setCreating(false); setEditing(null); }} />
        </Modal>
      ) : null}

      {deleting ? (
        <Modal title="Delete product?" description="This product will be removed from the catalog." onClose={() => !deleteBusy && setDeleting(null)} size="small">
          {deleteError ? <div className="form-message form-message--error" role="alert">{deleteError}</div> : null}
          <div className="confirm-record"><span className="confirm-record-label">PRODUCT</span><strong>{deleting.name}</strong><span>{deleting.sku_code}</span></div>
          <div className="form-actions">
            <button className="button button--quiet" type="button" onClick={() => setDeleting(null)} disabled={deleteBusy}>Cancel</button>
            <button className="button button--danger" type="button" onClick={confirmDelete} disabled={deleteBusy}>{deleteBusy ? "Deleting…" : "Delete product"}</button>
          </div>
        </Modal>
      ) : null}
    </section>
  );
}
