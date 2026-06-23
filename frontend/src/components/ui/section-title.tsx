interface SectionTitleProps {
  eyebrow: string;
  title: string;
  description: string;
}

export function SectionTitle({
  eyebrow,
  title,
  description,
}: SectionTitleProps) {
  return (
    <div style={{ display: "grid", gap: 14, maxWidth: 720 }}>
      <span className="section-label">{eyebrow}</span>
      <h2 style={{ margin: 0, fontSize: "clamp(2rem, 5vw, 3.5rem)" }}>{title}</h2>
      <p
        style={{
          margin: 0,
          color: "#9eb0cf",
          fontSize: "1.05rem",
          lineHeight: 1.7,
        }}
      >
        {description}
      </p>
    </div>
  );
}
