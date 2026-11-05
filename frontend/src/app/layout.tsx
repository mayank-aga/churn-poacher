import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import { Sidebar } from "@/components/layout/Sidebar";

export const metadata: Metadata = {
  title: "The Churn Poacher | Competitive Intelligence & Customer Acquisition",
  description: "Enterprise competitive takeout selling and account hijacking platform for Datadog to SigNoz / Grafana.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-foreground antialiased min-h-screen flex">
        <Providers>
          <Sidebar />
          <main className="flex-1 min-w-0 flex flex-col min-h-screen bg-background">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
