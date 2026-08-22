import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agentic IDE",
  description: "Open-source Agentic IDE and Software Factory",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen">{children}</body>
    </html>
  );
}
