-- Schema for H2 test database
-- This ensures tables exist before tests run

CREATE TABLE IF NOT EXISTS user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS player (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    position VARCHAR(10),
    team VARCHAR(100),
    fpl_id BIGINT,
    value DOUBLE DEFAULT 0.0,
    total_points INT DEFAULT 0,
    weekly_points INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS team (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    budget DOUBLE,
    user_id BIGINT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS team_players (
    team_id BIGINT,
    player_id BIGINT,
    PRIMARY KEY (team_id, player_id),
    FOREIGN KEY (team_id) REFERENCES team(id),
    FOREIGN KEY (player_id) REFERENCES player(id)
);

