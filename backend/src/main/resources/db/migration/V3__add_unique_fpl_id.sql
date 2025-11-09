-- Add UNIQUE constraint on fpl_id to enable UPSERT operations (PostgreSQL)
-- This ensures we can update existing players by fpl_id without breaking team references

CREATE UNIQUE INDEX IF NOT EXISTS idx_fpl_id ON player (fpl_id);

