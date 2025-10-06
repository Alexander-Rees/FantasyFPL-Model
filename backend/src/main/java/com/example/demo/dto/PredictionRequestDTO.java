package com.example.demo.dto;

import java.util.List;

public class PredictionRequestDTO {
    private Integer gameweek; // Optional: specific gameweek
    private List<Long> players; // Optional: specific players to predict
    
    public PredictionRequestDTO() {}
    
    public PredictionRequestDTO(Integer gameweek, List<Long> players) {
        this.gameweek = gameweek;
        this.players = players;
    }
    
    // Getters and setters
    public Integer getGameweek() {
        return gameweek;
    }
    
    public void setGameweek(Integer gameweek) {
        this.gameweek = gameweek;
    }
    
    public List<Long> getPlayers() {
        return players;
    }
    
    public void setPlayers(List<Long> players) {
        this.players = players;
    }
}
