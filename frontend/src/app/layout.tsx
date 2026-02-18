import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Thesis Engine",
  description: "AI-powered institutional stock research platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        {/* Navigation */}
        <nav className="sticky top-0 z-50 border-b border-[var(--color-border-light)] bg-[var(--color-surface)]/80 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <a href="/" className="group flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-sm transition-transform group-hover:scale-105">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <span className="text-xl font-semibold tracking-tight text-[var(--color-text-primary)]">
                Thesis Engine
              </span>
            </a>
            <div className="flex items-center gap-6">
              <a 
                href="/" 
                className="text-sm font-medium text-[var(--color-text-secondary)] transition-colors hover:text-[var(--color-primary)]"
              >
                Dashboard
              </a>
              <a 
                href="https://github.com/your-repo" 
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--color-text-secondary)] transition-colors hover:text-[var(--color-primary)]"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
            </div>
          </div>
        </nav>
        
        {/* Main content */}
        <main className="mx-auto max-w-7xl px-6 py-8">
          {children}
        </main>
        
        {/* Footer */}
        <footer className="mt-auto border-t border-[var(--color-border-light)] bg-[var(--color-surface)]">
          <div className="mx-auto max-w-7xl px-6 py-8">
            <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
              <p className="text-sm text-[var(--color-text-secondary)]">
                © 2026 Thesis Engine. AI-powered investment research.
              </p>
              <div className="flex items-center gap-6 text-sm text-[var(--color-text-secondary)]">
                <span className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                  System Operational
                </span>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
