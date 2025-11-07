-- Add UNIQUE constraint on fpl_id to enable UPSERT operations
-- This ensures we can update existing players by fpl_id without breaking team references

ALTER TABLE player 
  ADD UNIQUE INDEX idx_fpl_id (fpl_id);

