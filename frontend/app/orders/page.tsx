"use client";
import { useState } from "react";
import { apiFetch, getCurrentUserId } from "../lib/api";
import ReviewModal from "../components/ReviewModal";

interface Order {
  id: string;
  listing_id: string;
  buyer_id: string;
  seller_id: string;
  status: "requested" | "accepted" | "in_progress" | "delivered" | "confirmed" | "cancelled" | "disputed";
  payment_status: "pending" | "paid" | "failed" | "refunded";
  price_cents: number;
  commission_cents: number;
}

interface OrderAction {
  label: string;
  status: string;
  className: string;
  allowedRole: "buyer" | "seller" | "either";
}

function getAvailableActions(status: Order["status"]): OrderAction[] {
  switch (status) {
    case "requested":
      return [
        { label: "Accept", status: "accepted", className: "bg-emerald-600 hover:bg-emerald-700", allowedRole: "seller" },
        { label: "Cancel", status: "cancelled", className: "bg-rose-600 hover:bg-rose-700", allowedRole: "either" },
      ];
    case "accepted":
      return [
        { label: "Start Task", status: "in_progress", className: "bg-indigo-600 hover:bg-indigo-700", allowedRole: "seller" },
        { label: "Cancel", status: "cancelled", className: "bg-rose-600 hover:bg-rose-700", allowedRole: "either" },
      ];
    case "in_progress":
      return [
        { label: "Mark Delivered", status: "delivered", className: "bg-purple-600 hover:bg-purple-700", allowedRole: "seller" },
        { label: "Cancel", status: "cancelled", className: "bg-rose-600 hover:bg-rose-700", allowedRole: "either" },
      ];
    case "delivered":
      return [
        { label: "Confirm & Release Payout", status: "confirmed", className: "bg-green-600 hover:bg-green-700", allowedRole: "buyer" },
        { label: "Dispute", status: "disputed", className: "bg-orange-600 hover:bg-orange-700", allowedRole: "either" },
      ];
    case "disputed":
      return [
        { label: "Confirm & Release Payout", status: "confirmed", className: "bg-green-600 hover:bg-green-700", allowedRole: "buyer" },
        { label: "Cancel", status: "cancelled", className: "bg-rose-600 hover:bg-rose-700", allowedRole: "either" },
      ];
    default:
      return [];
  }
}

export default function OrdersPage() {
  const [orderIdInput, setOrderIdInput] = useState("");
  const [activeOrder, setActiveOrder] = useState<Order | null>(null);
  const [loadingOrder, setLoadingOrder] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [selectedOrderForReview, setSelectedOrderForReview] = useState<string | null>(null);

  const loadOrder = async () => {
    if (!orderIdInput.trim()) return;
    setError(null);
    setMessage(null);
    setLoadingOrder(true);

    try {
      const order = await apiFetch(`/orders/${orderIdInput.trim()}`);
      setActiveOrder(order);
    } catch (err: any) {
      setError(err.message || "Failed to load order.");
      setActiveOrder(null);
    } finally {
      setLoadingOrder(false);
    }
  };

  const updateOrderStatus = async (newStatus: string) => {
    if (!activeOrder) return;
    setError(null);
    setMessage(null);
    setUpdating(true);

    try {
      const updated = await apiFetch(`/orders/${activeOrder.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });

      setActiveOrder(updated);
      setMessage(`Order status updated to "${newStatus}" successfully!`);
    } catch (err: any) {
      setError(err.message || "Failed to update order status.");
    } finally {
      setUpdating(false);
    }
  };

  const currentUserId = getCurrentUserId();
  const isBuyer = activeOrder?.buyer_id === currentUserId;
  const isSeller = activeOrder?.seller_id === currentUserId;

  const availableActions = activeOrder
    ? getAvailableActions(activeOrder.status).filter((action) => {
        if (action.allowedRole === "either") return true;
        if (action.allowedRole === "buyer") return isBuyer;
        if (action.allowedRole === "seller") return isSeller;
        return false;
      })
    : [];

  const paymentNotYetConfirmed = activeOrder?.payment_status !== "paid";

  return (
    <div className="mx-auto max-w-2xl p-6">
      <h1 className="text-3xl font-bold tracking-tight">Manage Orders</h1>
      <p className="mt-1 text-sm text-gray-500">
        Enter an Order ID to manage status lifecycle transitions.
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
          onClick={loadOrder}
          disabled={loadingOrder}
          className="rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loadingOrder ? "Loading..." : "Load"}
        </button>
      </div>

      {activeOrder && (
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center justify-between border-b border-gray-100 pb-4 dark:border-zinc-800">
            <div>
              <p className="text-xs font-mono text-gray-400">Order ID: {activeOrder.id}</p>
              <p className="mt-1 text-lg font-bold">
                Status:{" "}
                <span className="uppercase text-blue-600">{activeOrder.status}</span>
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Payment:{" "}
                <span className="font-medium">{activeOrder.payment_status}</span>
                {" · "}
                ${(activeOrder.price_cents / 100).toFixed(2)} total
                {" "}
                (${(activeOrder.commission_cents / 100).toFixed(2)} platform fee)
              </p>
            </div>

            {activeOrder.status === "confirmed" && (
              <button
                onClick={() => setSelectedOrderForReview(activeOrder.id)}
                className="rounded-md bg-amber-500 px-3.5 py-2 text-xs font-semibold text-white hover:bg-amber-600"
              >
                Leave Review ⭐
              </button>
            )}
          </div>

          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Available Actions:
            </h3>

            {availableActions.length === 0 && (
              <p className="mt-2 text-sm text-gray-400">No further actions available for this order.</p>
            )}

            <div className="mt-3 flex flex-wrap gap-2">
              {availableActions.map((action) => {
                const isConfirmAction = action.status === "confirmed";
                const blockedByPayment = isConfirmAction && paymentNotYetConfirmed;

                return (
                  <button
                    key={action.status}
                    disabled={updating || blockedByPayment}
                    onClick={() => updateOrderStatus(action.status)}
                    title={blockedByPayment ? "Payment hasn't been confirmed yet" : undefined}
                    className={`rounded-md px-3.5 py-2 text-xs font-semibold text-white disabled:opacity-50 ${action.className}`}
                  >
                    {action.label}
                  </button>
                );
              })}
            </div>

            {availableActions.some((a) => a.status === "confirmed") && paymentNotYetConfirmed && (
              <p className="mt-2 text-xs text-amber-600">
                Payment hasn't been confirmed yet — confirming will fail until it has.
              </p>
            )}
          </div>
        </div>
      )}

      {selectedOrderForReview && (
        <ReviewModal
          orderId={selectedOrderForReview}
          onSuccess={() => {
            setSelectedOrderForReview(null);
            alert("Review submitted successfully!");
          }}
          onClose={() => setSelectedOrderForReview(null)}
        />
      )}
    </div>
  );
}