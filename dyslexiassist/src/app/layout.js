import "./globals.css";

export const metadata = {
  title: "DyslexiAssist",
  description: "AI-Powered Dyslexia Assistance",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="font-dyslexic antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
