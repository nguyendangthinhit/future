import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";

const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: "MarkX — Auto Video Platform",
  description: "Tự động tạo & đăng video ngắn lên Facebook và TikTok",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={outfit.variable}>
      <body className="font-sans antialiased text-slate-200">
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 sm:ml-64 relative">
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}
