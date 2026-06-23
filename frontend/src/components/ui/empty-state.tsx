interface EmptyStateProps {
  title: string;
  description: string;
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div
      style={{
        display: "grid",
        gap: 8,
        padding: 18,
        borderRadius: 18,
        border: "1px dashed rgba(123, 163, 255, 0.2)",
        background: "rgba(6, 16, 30, 0.45)",
      }}
    >
      <strong>{title}</strong>
      <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>{description}</p>
    </div>
  );
}
