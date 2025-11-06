-- Add missing columns to team table
-- Note: MySQL doesn't support IF NOT EXISTS in ALTER TABLE, but Flyway ensures this runs only once

ALTER TABLE team 
  ADD COLUMN budget DOUBLE,
  ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

