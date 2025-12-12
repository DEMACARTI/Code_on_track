-- Migration: Fix Vendors Schema (Add is_active)
-- Purpose: Add missing 'is_active' column to vendors table.
-- This was missed in Part 3 and is causing ORM queries to fail.

BEGIN;

ALTER TABLE vendors ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

COMMIT;
