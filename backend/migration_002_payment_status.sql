-- ============================================================
-- Migration 002: payment status tracking on orders
-- Run this in the Supabase SQL Editor -- additive only, safe to
-- run on the existing orders table.
-- ============================================================

alter table public.orders
  add column payment_status text not null default 'pending'
    check (payment_status in ('pending', 'paid', 'failed', 'refunded'));

create index orders_payment_status_idx on public.orders(payment_status);
