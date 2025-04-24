import { ThemeProvider } from "@/contexts/ThemeContext";
import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning={true} className="font-['OpenDyslexic']">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}