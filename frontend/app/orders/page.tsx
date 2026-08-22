"use client";

import { useState } from "react";
import { apiFetch } from "../lib/api";

interface Order {
  id: string;
  listing_id: string;
  buyer_id: string;
  seller_id: string;
  status: "requested" | "accepted" | "in_progress" | "delivered" | "confirmed" | "cancelled" | "disputed";
  amount_cents: number;
}

export default function OrdersPage() {
  const [orderIdInput, setOrderIdInput] = useState("");
  const [activeOrder, setActiveOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const updateOrderStatus = async (newStatus: string) => {
    if (!activeOrder) return;
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      // PATCH /orders/{order_id}
      const updated = await apiFetch(`/orders/${activeOrder.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });

      setActiveOrder(updated);
      setMessage(`Order status updated to "${newStatus}" successfully!`);
    } catch (err: any) {
      // Surface backend business rule error directly
      setError(err.message || "Failed to update order status.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl p-6">
      <h1 className="text-3xl font-bold tracking-tight">Manage Orders</h1>
      <p className="mt-1 text-sm text-gray-500">
        Enter an Order ID to manage status lifecycle transitions (Accept, Start, Deliver, Confirm, Cancel).
      </p>

      {error && (
        <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/50 dark:text-red-300 border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}

      {message && (
        <div className="mt-4 rounded-md bg-green-50 p-3 text-sm text-green-700 dark:bg-green-950/50 dark:text-green-300 border border-green-200 dark:border-green-800">
          {message}
        </div>
      )}

      <div className="mt-6 flex gap-3">
        <input
          type="text"
          placeholder="Paste Order UUID..."
          value={orderIdInput}
          onChange={(e) => setOrderIdInput(e.target.value)}
          className="w-full rounded-md border border-gray-300 p-2.5 text-sm dark:border-zinc-800 dark:bg-zinc-950"
        />
        <button
          onClick={() => {
            if (orderIdInput.trim()) {
              setActiveOrder({
                id: orderIdInput.trim(),
                listing_id: "listing-id",
                buyer_id: "buyer-id",
                seller_id: "seller-id",
                status: "requested",
                amount_cents: 2500,
              });
            }
          }}
          className="rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          Load
        </button>
      </div>

      {activeOrder && (
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center justify-between border-b border-gray-100 pb-4 dark:border-zinc-800">
            <div>
              <p className="text-xs font-mono text-gray-400">Order ID: {activeOrder.id}</p>
              <p className="mt-1 text-lg font-bold">
                Current Status:{" "}
                <span className="uppercase text-blue-600">{activeOrder.status}</span>
              </p>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Available Lifecycle Actions:
            </h3>

            <div className="mt-3 flex flex-wrap gap-2">
              <button
                disabled={loading}
                onClick={() => updateOrderStatus("accepted")}
                className="rounded-md bg-emerald-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                Seller: Accept
              </button>
              <button
                disabled={loading}
                onClick={() => updateOrderStatus("in_progress")}
                className="rounded-md bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                Seller: Start Task
              </button>
              <button
                disabled={loading}
                onClick={() => updateOrderStatus("delivered")}
                className="rounded-md bg-purple-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
              >
                Seller: Mark Delivered
              </button>
              <button
                disabled={loading}
                onClick={() => updateOrderStatus("confirmed")}
                className="rounded-md bg-green-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-green-700 disabled:opacity-50"
              >
                Buyer: Confirm & Release Payout
              </button>
              <button
                disabled={loading}
                onClick={() => updateOrderStatus("cancelled")}
                className="rounded-md bg-rose-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-rose-700 disabled:opacity-50"
              >
                Cancel / Refund
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}