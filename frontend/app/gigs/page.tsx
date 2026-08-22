"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "../lib/api";

interface Listing {
  id: string;
  seller_id: string;
  title: string;
  description?: string;
  price_cents: number;
  category: string;
  status: string;
}

export default function GigsPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadListings() {
      try {
        // GET /listings (public endpoint)
        const data = await apiFetch("/listings");
        setListings(data);
      } catch (err: any) {
        setError(err.message || "Failed to load listings");
      } finally {
        setLoading(false);
      }
    }

    loadListings();
  }, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl p-6 text-center text-gray-500">
        Loading campus gigs...
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <div className="rounded-md bg-red-50 p-4 text-red-700 dark:bg-red-950/50 dark:text-red-300">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl p-6">
      <h1 className="text-3xl font-bold tracking-tight">Available Gigs</h1>
      <p className="mt-1 text-gray-500">Browse and apply for tasks around campus.</p>

      {listings.length === 0 ? (
        <div className="mt-8 rounded-lg border border-dashed border-gray-300 p-8 text-center text-gray-500 dark:border-zinc-800">
          No active gigs found. Be the first to post one!
        </div>
      ) : (
        <div className="mt-6 flex flex-col gap-4">
          {listings.map((gig) => (
            <div
              key={gig.id}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
            >
              <div>
                <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                  {gig.category}
                </span>
                <h2 className="mt-2 text-xl font-semibold">{gig.title}</h2>
                {gig.description && (
                  <p className="mt-1 text-sm text-gray-500 line-clamp-1">
                    {gig.description}
                  </p>
                )}
              </div>
              <div className="text-right">
                {/* Remember: backend returns price in cents, divide by 100 for display */}
                <p className="text-xl font-bold text-green-600">
                  ${(gig.price_cents / 100).toFixed(2)}
                </p>
                <Link
                  href={`/gigs/${gig.id}`}
                  className="mt-2 inline-block rounded-md bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                >
                  View Details
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}