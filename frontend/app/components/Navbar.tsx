import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between border-b border-gray-200 bg-white px-8 py-4 dark:border-zinc-800 dark:bg-zinc-900">
      {/* Brand Logo */}
      <Link href="/" className="text-xl font-bold text-blue-600">
        QuadGig
      </Link>

      {/* Navigation Links */}
      <div className="flex items-center gap-6 text-sm font-medium">
        <Link href="/gigs" className="hover:text-blue-600">
          Browse Gigs
        </Link>
        <Link href="/post" className="hover:text-blue-600">
          Post a Task
        </Link>
        <Link
          href="/login"
          className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Sign In
        </Link>
      </div>
    </nav>
  );
}