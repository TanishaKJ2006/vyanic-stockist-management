import { NavLink } from "react-router";

import Icon from "../ui/Icon.jsx";

const navigation = [
  { label: "Dashboard", to: "/", icon: "dashboard", end: true },
  { label: "Products", to: "/products", icon: "products" },
  { label: "Stockists", to: "/stockists", icon: "stockists" },
  { label: "Audit logs", to: "/audit-logs", icon: "audit" },
];

function roleLabel(role) {
  if (role === "admin") return "Administrator";
  if (role === "stockist") return "Stockist · read only";
  return "Viewer · read only";
}

export default function Sidebar({ isOpen, onNavigate, onClose, user, onLogout }) {
  return (
    <aside className={`sidebar${isOpen ? " sidebar--open" : ""}`}>
      <div className="sidebar-brand">
        <div className="brand-mark" aria-hidden="true">
          <span>V</span>
          <i />
        </div>
        <div className="brand-copy">
          <span className="brand-name">Vyanic</span>
          <span className="brand-caption">TECHNOLOGIES</span>
        </div>
        <button
          className="icon-button sidebar-close"
          type="button"
          aria-label="Close navigation"
          onClick={onClose}
        >
          <Icon name="close" size={19} />
        </button>
      </div>

      <div className="sidebar-label">WORKSPACE</div>
      <nav id="main-navigation" className="sidebar-nav" aria-label="Main navigation">
        {navigation.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            className={({ isActive }) =>
              `nav-link${isActive ? " nav-link--active" : ""}`
            }
          >
            <Icon name={item.icon} size={19} />
            <span>{item.label}</span>
            <span className="nav-link-indicator" />
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-divider" />
        <div className="workspace-note">
          <span className="workspace-note-mark">
            <Icon name="sparkle" size={17} />
          </span>
          <span>
            <strong>Stockist Portal</strong>
            <small>Internal workspace</small>
          </span>
        </div>
        <div className="sidebar-account">
          <span className="sidebar-account-avatar" aria-hidden="true">
            {user?.name?.trim()?.charAt(0)?.toUpperCase() ?? "V"}
          </span>
          <span className="sidebar-account-copy">
            <strong>{user?.name ?? "Signed-in user"}</strong>
            <small>{roleLabel(user?.role)}</small>
          </span>
          <button
            className="sidebar-signout"
            type="button"
            onClick={onLogout}
            aria-label="Sign out"
            title="Sign out"
          >
            <Icon name="logout" size={17} />
          </button>
        </div>
        <div className="sidebar-version">VYANIC · OPERATIONS</div>
      </div>
    </aside>
  );
}
