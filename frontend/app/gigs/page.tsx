const mockGigs = [
  { id: 1, title: "Help move dorm furniture", price: "$30", location: "West Hall", category: "Labor" },
  { id: 2, title: "CS101 Python Tutor Needed", price: "$25/hr", location: "Library", category: "Tutoring" },
  { id: 3, title: "Campus Event Photographer", price: "$50", location: "Student Union", category: "Events" },
];

export default function GigsPage() {
  return (
    <div className="mx-auto max-w-4xl p-6">
      <h1 className="text-3xl font-bold tracking-tight">Available Gigs</h1>
      <p className="mt-1 text-gray-500">Browse and apply for tasks around campus.</p>

      <div className="mt-6 flex flex-col gap-4">
        {mockGigs.map((gig) => (
          <div key={gig.id} className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <div>
              <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                {gig.category}
              </span>
              <h2 className="mt-2 text-xl font-semibold">{gig.title}</h2>
              <p className="text-sm text-gray-500">{gig.location}</p>
            </div>
            <div className="text-right">
              <p className="text-xl font-bold text-green-600">{gig.price}</p>
              <button className="mt-2 rounded-md bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700">
                Apply
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}