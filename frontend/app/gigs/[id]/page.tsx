"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/app/lib/api";

interface Listing {
  id: string;
  seller_id: string;
  title: string;
  description?: string;
  price_cents: number;
  category: string;
  status: string;
}

export default function GigDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();

  const [listing, setListing] = useState<Listing | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadListing() {
      try {
        // GET /listings/{id} (public)
        const data = await apiFetch(`/listings/${id}`);
        setListing(data);
      } catch (err: any) {
        setError(err.message || "Failed to load gig details.");
      } finally {
        setLoading(false);
      }
    }

    loadListing();
  }, [id]);

  const handleOrder = async () => {
    setError(null);
    setSubmitting(true);

    try {
      // POST /orders (auth required)
      const res = await apiFetch("/orders", {
        method: "POST",
        body: JSON.stringify({ listing_id: id }),
      });

      // Backend returns order info + client_secret for Stripe checkout
      alert(`Order created successfully! Order ID: ${res.id || res.order_id || "Success"}`);
    } catch (err: any) {
      // Direct display of backend error detail (e.g. "You can't order your own listing.")
      setError(err.message || "Could not place order.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl p-6 text-center text-gray-500">
        Loading gig details...
      </div>
    );
  }

  if (error && !listing) {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <div className="rounded-md bg-red-50 p-4 text-red-700 dark:bg-red-950/50 dark:text-red-300">
          {error}
        </div>
        <Link href="/gigs" className="mt-4 inline-block text-sm text-blue-600 hover:underline">
          ← Back to all gigs
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl p-6">
      <Link href="/gigs" className="text-sm font-medium text-blue-600 hover:underline">
        ← Back to all gigs
      </Link>

      {error && (
        <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/50 dark:text-red-300 border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}

      {listing && (
        <div className="mt-4 rounded-xl border border-gray-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center justify-between">
            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-950 dark:text-blue-300">
              {listing.category}
            </span>
            <span className="text-2xl font-bold text-green-600">
              ${(listing.price_cents / 100).toFixed(2)}
            </span>
          </div>

          <h1 className="mt-4 text-3xl font-bold tracking-tight">{listing.title}</h1>

          <div className="mt-6 border-t border-gray-100 pt-4 dark:border-zinc-800">
            <h2 className="text-sm font-semibold text-gray-900 dark:text-zinc-200">
              Task Description
            </h2>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {listing.description || "No description provided."}
            </p>
          </div>

          <button
            onClick={handleOrder}
            disabled={submitting}
            className="mt-8 w-full rounded-md bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? "Processing..." : "Order / Apply for this Gig"}
          </button>
        </div>
      )}
    </div>
  );
}