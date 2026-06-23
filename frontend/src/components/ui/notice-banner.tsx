interface NoticeBannerProps {
  title: string;
  description: string;
  tone?: "info" | "success" | "warning";
}

export function NoticeBanner({
  title,
  description,
  tone = "info",
}: NoticeBannerProps) {
  const colors = {
    info: {
      background: "rgba(104, 213, 255, 0.08)",
      border: "rgba(104, 213, 255, 0.2)",
      text: "#d8f7ff",
    },
    success: {
      background: "rgba(61, 214, 160, 0.08)",
      border: "rgba(61, 214, 160, 0.2)",
      text: "#dffcf0",
    },
    warning: {
      background: "rgba(255, 179, 87, 0.08)",
      border: "rgba(255, 179, 87, 0.2)",
      text: "#fff1d8",
    },
  };

  return (
    <div
      style={{
        display: "grid",
        gap: 8,
        padding: 16,
        borderRadius: 18,
        background: colors[tone].background,
        border: `1px solid ${colors[tone].border}`,
        color: colors[tone].text,
      }}
    >
      <strong>{title}</strong>
      <p style={{ margin: 0, color: "inherit", lineHeight: 1.7 }}>{description}</p>
    </div>
  );
}
