import './globals.css';
import type { Metadata } from 'next';
import { NavBar } from '@/components/NavBar';
import { Disclaimer } from '@/components/Disclaimer';

export const metadata: Metadata = {
  title: 'LexBridge',
  description: 'Comparative US/Venezuela legal learning platform'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-4 px-4 py-6">
          <header className="space-y-4">
            <h1 className="text-3xl font-bold">LexBridge</h1>
            <NavBar />
            <Disclaimer />
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
