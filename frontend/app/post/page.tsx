"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "../lib/api";

export default function PostGigPage() {
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [category, setCategory] = useState("Tutoring");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const priceNum = parseFloat(price);
    if (isNaN(priceNum) || priceNum <= 0) {
      setError("Please enter a valid price greater than $0.");
      return;
    }

    setLoading(true);

    try {
      // POST /listings (auth required)
      // Prices MUST be sent in cents to the backend
      const res = await apiFetch("/listings", {
        method: "POST",
        body: JSON.stringify({
          title,
          description: description || undefined,
          price_cents: Math.round(priceNum * 100),
          category,
        }),
      });

      // Redirect to the newly created gig or feed
      if (res.id) {
        router.push(`/gigs/${res.id}`);
      } else {
        router.push("/gigs");
      }
    } catch (err: any) {
      setError(err.message || "Failed to create listing.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-xl p-6">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
        Post a Campus Gig
      </h1>
      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
        Describe what you need help with or what service you are offering to fellow students.
      </p>

      {error && (
        <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/50 dark:text-red-300 border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-6 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Gig Title *
          </label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Calculus II Tutoring / Moving Couch"
            className="mt-1 w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-950"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Category *
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="mt-1 w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-950"
          >
            <option value="Tutoring">Tutoring</option>
            <option value="Moving">Moving & Labor</option>
            <option value="Tech Support">Tech Support</option>
            <option value="Events">Events & Photography</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Price ($ USD) *
          </label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            required
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            placeholder="25.00"
            className="mt-1 w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-950"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Description
          </label>
          <textarea
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Provide details on location, time frame, expectations..."
            className="mt-1 w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-950"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-blue-600 py-3 font-semibold text-white shadow hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Publishing Gig..." : "Publish Gig"}
        </button>
      </form>
    </div>
  );
}