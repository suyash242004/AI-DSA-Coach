import type { Metadata } from "next";
import "./globals.css";
import { AppProvider } from "@/lib/context";

export const metadata: Metadata = {
  title: "AI DSA Coach — Multi-Agent Learning Platform",
  description:
    "Master Data Structures & Algorithms with intelligent multi-agent AI coaching. Powered by Mentor, Code, Evaluation, and Orchestrator agents.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-mesh min-h-screen">
        <AppProvider>{children}</AppProvider>
      </body>
    </html>
  );
}
