package com.example.demo.dto;

import java.util.List;

public class PredictionResponseDTO {
    private List<PlayerPredictionDTO> predictions;
    private Integer gameweek;
    
    public PredictionResponseDTO() {}
    
    public PredictionResponseDTO(List<PlayerPredictionDTO> predictions, Integer gameweek) {
        this.predictions = predictions;
        this.gameweek = gameweek;
    }
    
    // Getters and setters
    public List<PlayerPredictionDTO> getPredictions() {
        return predictions;
    }
    
    public void setPredictions(List<PlayerPredictionDTO> predictions) {
        this.predictions = predictions;
    }
    
    public Integer getGameweek() {
        return gameweek;
    }
    
    public void setGameweek(Integer gameweek) {
        this.gameweek = gameweek;
    }
}
