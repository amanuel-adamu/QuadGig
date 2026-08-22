import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-6 text-gray-900 dark:bg-zinc-950 dark:text-zinc-100">
      <main className="flex w-full max-w-2xl flex-col items-center gap-6 text-center">
        {/* QuadGig Header */}
        <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-950 dark:text-blue-300">
          Campus Marketplace
        </span>
        
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl">
          QuadGig
        </h1>
        
        <p className="max-w-md text-lg text-gray-600 dark:text-gray-400">
          Find student gigs, hire campus help, and get tasks done fast.
        </p>

        {/* Action Buttons connected to routes */}
        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <Link
            href="/gigs"
            className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white shadow-md transition hover:bg-blue-700"
          >
            Browse Gigs
          </Link>
          <Link
            href="/post"
            className="rounded-lg border border-gray-300 bg-white px-6 py-3 font-semibold text-gray-700 shadow-sm transition hover:bg-gray-100 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
          >
            Post a Task
          </Link>
        </div>
      </main>
    </div>
  );
}