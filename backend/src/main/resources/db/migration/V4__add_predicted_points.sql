-- Add predicted_points column to player table (PostgreSQL)

ALTER TABLE player
ADD COLUMN IF NOT EXISTS predicted_points DOUBLE PRECISION DEFAULT 0;
