-- Add missing columns to team table (PostgreSQL)
-- Flyway ensures this runs only once
-- Only run if team table exists (created by V1)

-- Create trigger function for updated_at (PostgreSQL doesn't support ON UPDATE)
-- This function can be created even if team table doesn't exist yet
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$ language 'plpgsql';

-- Add columns and create trigger only if team table exists
-- All statements that reference 'team' table must be inside the DO block
DO $body$
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'team') THEN
    -- Add columns
    ALTER TABLE team 
      ADD COLUMN IF NOT EXISTS budget DOUBLE PRECISION,
      ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    
    -- Drop and create trigger (all inside the conditional)
    DROP TRIGGER IF EXISTS update_team_updated_at ON team;
    CREATE TRIGGER update_team_updated_at
        BEFORE UPDATE ON team
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
  END IF;
END $body$;

