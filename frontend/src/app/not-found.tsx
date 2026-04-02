import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Page Not Found",
};

export default function NotFound() {
  return (
    <div className="mx-auto max-w-lg px-6 py-24 text-center page-enter">
      <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-muted mb-6">
        <span className="text-3xl font-bold text-muted-foreground">404</span>
      </div>
      <h1 className="text-2xl font-bold mb-3">Page Not Found</h1>
      <p className="text-muted-foreground mb-8">
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <div className="flex gap-3 justify-center">
        <Link
          href="/"
          className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Analyze Content
        </Link>
        <Link
          href="/dashboard"
          className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-muted transition-colors"
        >
          Dashboard
        </Link>
      </div>
    </div>
  );
}
