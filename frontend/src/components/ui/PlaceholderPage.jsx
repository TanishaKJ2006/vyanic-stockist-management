import EmptyState from "./EmptyState.jsx";
import PageHeading from "./PageHeading.jsx";

export default function PlaceholderPage({
  eyebrow,
  title,
  description,
  icon,
  emptyTitle,
  emptyDescription,
}) {
  return (
    <section className="page-section">
      <PageHeading eyebrow={eyebrow} title={title} description={description} />
      <div className="content-card placeholder-card">
        <EmptyState
          icon={icon}
          title={emptyTitle}
          description={emptyDescription}
        />
      </div>
    </section>
  );
}
