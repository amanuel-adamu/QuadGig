import Link from "next/link";

export default async function GigDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="mx-auto max-w-2xl p-6">
      <Link href="/gigs" className="text-sm font-medium text-blue-600 hover:underline">
        ← Back to all gigs
      </Link>

      <div className="mt-4 rounded-xl border border-gray-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex items-center justify-between">
          <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-950 dark:text-blue-300">
            Gig #{id}
          </span>
          <span className="text-2xl font-bold text-green-600">$30</span>
        </div>

        <h1 className="mt-4 text-3xl font-bold tracking-tight">Move dorm furniture</h1>
        <p className="mt-2 text-sm text-gray-500">Posted 2 hours ago • West Hall</p>

        <div className="mt-6 border-t border-gray-100 pt-4 dark:border-zinc-800">
          <h2 className="text-sm font-semibold text-gray-900 dark:text-zinc-200">Task Description</h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Need someone strong to help move a desk, dressers, and bed frame up two flights of stairs in West Hall. Should take around an hour.
          </p>
        </div>

        <button className="mt-8 w-full rounded-md bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700">
          Apply for this Gig
        </button>
      </div>
    </div>
  );
}