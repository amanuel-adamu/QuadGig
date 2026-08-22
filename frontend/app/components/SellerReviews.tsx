"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

interface Review {
  id: string;
  rating: number;
  comment?: string;
  created_at?: string;
}

interface ReviewData {
  reviews: Review[];
  review_count: number;
  average_rating: number;
}

export default function SellerReviews({ sellerId }: { sellerId: string }) {
  const [data, setData] = useState<ReviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchReviews() {
      try {
        const res = await apiFetch(`/users/${sellerId}/reviews`);
        setData(res);
      } catch (err) {
        // Handle silenty if user has no reviews yet
      } finally {
        setLoading(false);
      }
    }

    if (sellerId) fetchReviews();
  }, [sellerId]);

  if (loading) return <div className="text-xs text-gray-400">Loading seller reviews...</div>;
  if (!data || data.review_count === 0) return null;

  return (
    <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center gap-3">
        <span className="text-2xl font-bold text-amber-500">
          ★ {data.average_rating.toFixed(1)}
        </span>
        <span className="text-sm text-gray-500">
          ({data.review_count} {data.review_count === 1 ? "review" : "reviews"})
        </span>
      </div>

      <div className="mt-4 space-y-3">
        {data.reviews.map((rev) => (
          <div key={rev.id} className="border-t border-gray-100 pt-3 dark:border-zinc-800">
            <div className="text-xs text-amber-500">{"★".repeat(rev.rating)}</div>
            {rev.comment && (
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{rev.comment}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}