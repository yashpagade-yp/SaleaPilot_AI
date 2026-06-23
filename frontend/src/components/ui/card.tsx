import type { CSSProperties, PropsWithChildren } from "react";

interface CardProps {
  style?: CSSProperties;
}

export function Card({ children, style }: PropsWithChildren<CardProps>) {
  return (
    <div
      className="panel"
      style={{
        padding: 24,
        ...style,
      }}
    >
      {children}
    </div>
  );
}
