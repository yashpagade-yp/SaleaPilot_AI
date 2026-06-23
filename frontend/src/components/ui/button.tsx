import type { ButtonHTMLAttributes, CSSProperties, PropsWithChildren } from "react";
import { Link } from "react-router-dom";

type ButtonVariant = "primary" | "secondary" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  fullWidth?: boolean;
  to?: string;
  href?: string;
  target?: string;
  rel?: string;
}

export function Button({
  children,
  variant = "primary",
  fullWidth = false,
  style,
  to,
  href,
  target,
  rel,
  ...props
}: PropsWithChildren<ButtonProps>) {
  const backgroundByVariant: Record<ButtonVariant, string> = {
    primary: "linear-gradient(135deg, #68d5ff 0%, #8b7cff 100%)",
    secondary: "rgba(18, 33, 57, 0.92)",
    ghost: "transparent",
  };

  const borderByVariant: Record<ButtonVariant, string> = {
    primary: "1px solid rgba(255,255,255,0.14)",
    secondary: "1px solid rgba(123, 163, 255, 0.2)",
    ghost: "1px solid transparent",
  };

  const colorByVariant: Record<ButtonVariant, string> = {
    primary: "#06101e",
    secondary: "#eff4ff",
    ghost: "#9eb0cf",
  };

  const sharedStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
    width: fullWidth ? "100%" : undefined,
    padding: "14px 18px",
    borderRadius: 16,
    border: borderByVariant[variant],
    background: backgroundByVariant[variant],
    color: colorByVariant[variant],
    fontWeight: 700,
    transition: "transform 0.2s ease, opacity 0.2s ease, border-color 0.2s ease",
    boxShadow: variant === "primary" ? "0 10px 30px rgba(104, 213, 255, 0.22)" : "none",
    ...style,
  };

  if (to) {
    return (
      <Link to={to} style={sharedStyle}>
        {children}
      </Link>
    );
  }

  if (href) {
    return (
      <a href={href} target={target} rel={rel} style={sharedStyle}>
        {children}
      </a>
    );
  }

  return (
    <button {...props} style={sharedStyle}>
      {children}
    </button>
  );
}
