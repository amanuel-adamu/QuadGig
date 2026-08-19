export default function LoginPage() {
  return (
    <div className="flex min-h-[80vh] items-center justify-center p-6">
      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <h1 className="text-2xl font-bold tracking-tight text-center">Welcome Back</h1>
        <p className="mt-1 text-center text-sm text-gray-500">
          Sign in with your campus email to continue
        </p>

        <form className="mt-6 flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium">Campus Email</label>
            <input
              type="email"
              placeholder="student@university.edu"
              className="mt-1 w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-900"
            />
          </div>

          <div>
            <label className="block text-sm font-medium">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="mt-1 w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-900"
            />
          </div>

          <button
            type="submit"
            className="mt-2 rounded-md bg-blue-600 py-2.5 font-semibold text-white hover:bg-blue-700"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}