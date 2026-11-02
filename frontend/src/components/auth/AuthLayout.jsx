import Icon from "../ui/Icon.jsx";

export default function AuthLayout({ children }) {
  return (
    <main className="auth-page">
      <aside className="auth-story" aria-label="Vyanic Technologies">
        <div className="auth-story-orbit auth-story-orbit--outer" />
        <div className="auth-story-orbit auth-story-orbit--inner" />
        <div className="auth-brand">
          <span className="auth-brand-mark">V<i /></span>
          <span>
            <strong>Vyanic</strong>
            <small>TECHNOLOGIES</small>
          </span>
        </div>
        <div className="auth-story-copy">
          <span className="auth-kicker"><Icon name="sparkle" size={15} /> STOCKIST MANAGEMENT</span>
          <h1>Built around the people who move your business forward.</h1>
          <p>One considered workspace for your products, stockists, and the places they serve.</p>
        </div>
        <div className="auth-story-footnote">VYANIC TECHNOLOGIES <span>·</span> OPERATIONS</div>
      </aside>

      <section className="auth-form-panel">
        <div className="auth-mobile-brand" aria-label="Vyanic Technologies">
          <span className="auth-brand-mark">V<i /></span>
          <span>
            <strong>Vyanic</strong>
            <small>TECHNOLOGIES</small>
          </span>
        </div>
        <div className="auth-form-content">{children}</div>
        <p className="auth-panel-footer">A focused workspace for thoughtful operations.</p>
      </section>
    </main>
  );
}
