package com.example.demo.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true) // This annotation tells Jackson to ignore unknown fields
public class PlayerStatisticsDTO {
    private GamesDTO games;

    // Getters and setters
    public GamesDTO getGames() {
        return games;
    }

    public void setGames(GamesDTO games) {
        this.games = games;
    }
}
