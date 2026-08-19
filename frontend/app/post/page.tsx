export default function PostGigPage() {
  return (
    <div className="mx-auto max-w-xl p-6">
      <h1 className="text-3xl font-bold tracking-tight">Post a New Gig</h1>
      <p className="mt-1 text-gray-500">Need help on campus? Fill out the details below.</p>

      <form className="mt-6 flex flex-col gap-4">
        <div>
          <label className="block text-sm font-medium">Gig Title</label>
          <input
            type="text"
            placeholder="e.g. Need help moving dorm boxes"
            className="mt-1 w-full rounded-md border border-gray-300 p-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Category</label>
          <select className="mt-1 w-full rounded-md border border-gray-300 p-2 text-sm dark:border-zinc-800 dark:bg-zinc-900">
            <option>Labor</option>
            <option>Tutoring</option>
            <option>Events</option>
            <option>Other</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium">Pay Amount</label>
          <input
            type="text"
            placeholder="e.g. $25 or $15/hr"
            className="mt-1 w-full rounded-md border border-gray-300 p-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
          />
        </div>

        <button
          type="submit"
          className="mt-2 rounded-md bg-blue-600 py-2.5 font-semibold text-white hover:bg-blue-700"
        >
          Publish Gig
        </button>
      </form>
    </div>
  );
}