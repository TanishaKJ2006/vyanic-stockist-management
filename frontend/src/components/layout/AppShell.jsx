import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router";

import Icon from "../ui/Icon.jsx";
import Sidebar from "./Sidebar.jsx";
import { useAuth } from "../../contexts/AuthContext.jsx";

const pageNames = {
  "/": "Dashboard",
  "/products": "Products",
  "/stockists": "Stockists",
  "/audit-logs": "Audit logs",
};

export default function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pageName = pageNames[location.pathname] ?? "Dashboard";
  const currentDate = new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  }).format(new Date());

  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  useEffect(() => {
    if (!sidebarOpen) return undefined;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") setSidebarOpen(false);
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [sidebarOpen]);

  return (
    <div className="app-frame">
      <button
        type="button"
        className={`mobile-scrim${sidebarOpen ? " mobile-scrim--visible" : ""}`}
        aria-label="Close navigation menu"
        aria-hidden={!sidebarOpen}
        tabIndex={sidebarOpen ? 0 : -1}
        onClick={() => setSidebarOpen(false)}
      />
      <Sidebar
        isOpen={sidebarOpen}
        onNavigate={() => setSidebarOpen(false)}
        onClose={() => setSidebarOpen(false)}
        user={user}
        onLogout={handleLogout}
      />

      <div className="app-main">
        <header className="topbar">
          <button
            className="icon-button mobile-menu-button"
            type="button"
            aria-label="Open navigation"
            aria-expanded={sidebarOpen}
            aria-controls="main-navigation"
            onClick={() => setSidebarOpen(true)}
          >
            <Icon name="menu" size={21} />
          </button>
          <div className="topbar-location">
            <span>OPERATIONS</span>
            <span className="topbar-slash">/</span>
            <strong>{pageName}</strong>
          </div>
          <div className="topbar-meta">
            <span className="workspace-status">
              <span className="status-dot" />
              Local workspace
            </span>
            <span className="topbar-date">
              <Icon name="calendar" size={16} />
              {currentDate}
            </span>
          </div>
        </header>

        <main className="main-content">
          <div key={location.pathname} className="page-transition">
            <Outlet />
          </div>
        </main>

        <footer className="app-footer">
          <span>© {new Date().getFullYear()} Vyanic Technologies</span>
          <span>Thoughtful stockist operations</span>
        </footer>
      </div>
    </div>
  );
}
