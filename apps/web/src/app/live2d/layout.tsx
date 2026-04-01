import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "じょぎナビ Live2D",
};

export default function Live2DLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
