import Image from "next/image";
import Link from "next/link";

/**
 * Header component with logo and navigation.
 * Displays the application logo prominently with accessibility attributes.
 */
export function Header() {
  return (
    <header className="border-b p-4">
      <div className="container mx-auto flex items-center gap-4">
        <Link href="/" className="flex items-center gap-2" aria-label="Site RAG Chatbot Home">
          <Image
            src="/logo.svg"
            alt="Site RAG Chatbot Logo"
            width={120}
            height={40}
            priority
            className="h-8 w-auto"
            aria-hidden="false"
          />
        </Link>
        <div className="flex-1" />
        <nav className="flex gap-4">
          <Link
            href="/"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Chat
          </Link>
          <Link
            href="/admin"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Admin
          </Link>
        </nav>
      </div>
    </header>
  );
}

