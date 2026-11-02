export default function PageHeading({ eyebrow, title, description, children }) {
  return (
    <div className="page-heading">
      <div className="page-heading-copy">
        {eyebrow ? <div className="eyebrow">{eyebrow}</div> : null}
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
      </div>
      {children ? <div className="page-heading-actions">{children}</div> : null}
    </div>
  );
}
