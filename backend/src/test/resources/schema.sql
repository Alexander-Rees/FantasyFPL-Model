-- Test schema for H2 database
-- Create all tables needed for tests
-- H2 with NON_KEYWORDS=USER in URL allows 'user' as table name without quotes
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

CREATE TABLE IF NOT EXISTS team (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  user_id BIGINT,
  CONSTRAINT fk_team_user FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE TABLE IF NOT EXISTS team_players (
  team_id BIGINT,
  player_id BIGINT,
  PRIMARY KEY (team_id, player_id),
  CONSTRAINT fk_tp_team FOREIGN KEY (team_id) REFERENCES team(id),
  CONSTRAINT fk_tp_player FOREIGN KEY (player_id) REFERENCES player(id)
);

