interface MetricCardProps {
  label: string;
  value: string;
  helper: string;
}

export function MetricCard({ label, value, helper }: MetricCardProps) {
  return (
    <div
      style={{
        padding: 18,
        borderRadius: 20,
        background: "rgba(6, 16, 30, 0.72)",
        border: "1px solid rgba(123, 163, 255, 0.14)",
        display: "grid",
        gap: 8,
      }}
    >
      <span style={{ color: "#9eb0cf" }}>{label}</span>
      <strong style={{ fontSize: "1.8rem", lineHeight: 1 }}>{value}</strong>
      <p style={{ margin: 0, color: "#73839d", lineHeight: 1.6 }}>{helper}</p>
    </div>
  );
}
