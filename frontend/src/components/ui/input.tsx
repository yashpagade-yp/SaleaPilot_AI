import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
}

export function Input({ label, hint, style, ...props }: InputProps) {
  return (
    <label style={{ display: "grid", gap: 10 }}>
      <span style={{ color: "#eff4ff", fontWeight: 600 }}>{label}</span>
      <input
        {...props}
        style={{
          borderRadius: 16,
          border: "1px solid rgba(123, 163, 255, 0.18)",
          background: "rgba(6, 16, 30, 0.8)",
          color: "#eff4ff",
          padding: "14px 16px",
          outline: "none",
          ...style,
        }}
      />
      {hint ? (
        <span style={{ color: "#73839d", fontSize: "0.9rem" }}>{hint}</span>
      ) : null}
    </label>
  );
}
