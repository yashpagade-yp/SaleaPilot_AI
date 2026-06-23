interface StatusPillProps {
  label: string;
  tone?: "neutral" | "success" | "warning";
}

export function StatusPill({ label, tone = "neutral" }: StatusPillProps) {
  const colors = {
    neutral: {
      background: "rgba(104, 213, 255, 0.1)",
      color: "#9bdcff",
    },
    success: {
      background: "rgba(61, 214, 160, 0.12)",
      color: "#69eab5",
    },
    warning: {
      background: "rgba(255, 179, 87, 0.12)",
      color: "#ffc878",
    },
  };

  return (
    <span
      style={{
        display: "inline-flex",
        padding: "8px 12px",
        borderRadius: 999,
        fontSize: "0.85rem",
        fontWeight: 700,
        ...colors[tone],
      }}
    >
      {label}
    </span>
  );
}
