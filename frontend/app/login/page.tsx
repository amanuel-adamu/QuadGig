"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      if (isSignUp) {
        // POST /auth/signup
        const res = await apiFetch("/auth/signup", {
          method: "POST",
          body: JSON.stringify({
            email,
            password,
            display_name: displayName,
          }),
        });
        setMessage(res.message || "Signup successful! Check your inbox to verify your .edu email.");
      } else {
        // POST /auth/login
        const res = await apiFetch("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });

        // Store access token
        if (res.access_token) {
          localStorage.setItem("access_token", res.access_token);
          if (res.user_id) localStorage.setItem("user_id", res.user_id);
          router.push("/gigs");
        }
      }
    } catch (err: any) {
      // Direct display of backend exact error detail (e.g. 403 unverified, 400 non-.edu)
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[80vh] flex-col justify-center px-6 py-12 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
          {isSignUp ? "Create your account" : "Sign in to QuadGig"}
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Must use a valid campus (.edu) email address.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white px-6 py-8 shadow-sm rounded-xl border border-gray-200 dark:bg-zinc-900 dark:border-zinc-800">
          {error && (
            <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/50 dark:text-red-300 border border-red-200 dark:border-red-800">
              {error}
            </div>
          )}

          {message && (
            <div className="mb-4 rounded-md bg-green-50 p-3 text-sm text-green-700 dark:bg-green-950/50 dark:text-green-300 border border-green-200 dark:border-green-800">
              {message}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            {isSignUp && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Display Name
                </label>
                <input
                  type="text"
                  required
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="e.g. Alex Smith"
                  className="mt-1 w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-950"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Campus Email (.edu)
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="student@university.edu"
                className="mt-1 w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-950"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1 w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-950"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-blue-600 py-3 text-sm font-semibold text-white shadow hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Processing..." : isSignUp ? "Sign Up" : "Sign In"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm">
            <button
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError(null);
                setMessage(null);
              }}
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              {isSignUp
                ? "Already have an account? Sign in"
                : "Don't have an account? Sign up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}