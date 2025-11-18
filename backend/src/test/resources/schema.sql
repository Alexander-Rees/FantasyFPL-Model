-- Test schema for H2 database
-- Create all tables needed for tests in correct order (dependencies first)
-- H2 with NON_KEYWORDS=USER in URL allows 'user' as table name
-- Disable referential integrity during creation, then enable it
SET REFERENTIAL_INTEGRITY FALSE;

-- Create base tables first (no foreign keys)
-- H2 with NON_KEYWORDS=USER allows 'user' without quotes in CREATE TABLE
-- But we need to use quotes in ALTER TABLE for foreign keys
CREATE TABLE IF NOT EXISTS "user" (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS player (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  position VARCHAR(16),
  team VARCHAR(255),
  fpl_id BIGINT,
  value DOUBLE PRECISION,
  total_points INT,
  weekly_points INT
);

-- Create dependent tables
CREATE TABLE IF NOT EXISTS team (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  user_id BIGINT,
  budget DOUBLE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS team_players (
  team_id BIGINT,
  player_id BIGINT,
  PRIMARY KEY (team_id, player_id)
);

-- Now add foreign key constraints
ALTER TABLE team ADD CONSTRAINT fk_team_user FOREIGN KEY (user_id) REFERENCES "user"(id);
ALTER TABLE team_players ADD CONSTRAINT fk_tp_team FOREIGN KEY (team_id) REFERENCES team(id);
ALTER TABLE team_players ADD CONSTRAINT fk_tp_player FOREIGN KEY (player_id) REFERENCES player(id);

-- Re-enable referential integrity
SET REFERENTIAL_INTEGRITY TRUE;

