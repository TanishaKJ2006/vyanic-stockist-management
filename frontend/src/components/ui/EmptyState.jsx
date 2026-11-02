import Icon from "./Icon.jsx";

export default function EmptyState({ icon = "empty", title, description }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        <Icon name={icon} size={23} strokeWidth={1.6} />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}
