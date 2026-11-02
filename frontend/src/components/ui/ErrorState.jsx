import Icon from "./Icon.jsx";

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="state-panel state-panel--error" role="alert">
      <span className="state-panel-icon"><Icon name="warning" size={19} /></span>
      <div>
        <strong>We couldn’t load this information</strong>
        <p>{message}</p>
        {onRetry ? <button className="text-button" type="button" onClick={onRetry}>Try again</button> : null}
      </div>
    </div>
  );
}
