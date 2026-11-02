import Icon from "./Icon.jsx";

export default function AccessNotice() {
  return (
    <div className="access-notice" role="note">
      <Icon name="shield" size={17} />
      <span>You have read-only access. Contact a portal administrator to make changes.</span>
    </div>
  );
}
