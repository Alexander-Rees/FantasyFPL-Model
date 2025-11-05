-- Flyway baseline migration
CREATE TABLE IF NOT EXISTS user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS player (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  position VARCHAR(16),
  team VARCHAR(255),
  fpl_id BIGINT,
  value DOUBLE,
  total_points INT,
  weekly_points INT
);

CREATE TABLE IF NOT EXISTS team (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  user_id BIGINT,
  CONSTRAINT fk_team_user FOREIGN KEY (user_id) REFERENCES user(id)
);

-- join table for team players if not exists
CREATE TABLE IF NOT EXISTS team_players (
  team_id BIGINT,
  player_id BIGINT,
  PRIMARY KEY (team_id, player_id),
  CONSTRAINT fk_tp_team FOREIGN KEY (team_id) REFERENCES team(id),
  CONSTRAINT fk_tp_player FOREIGN KEY (player_id) REFERENCES player(id)
);

