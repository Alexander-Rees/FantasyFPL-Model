package com.example.demo.dto;

public class PlayerPredictionDTO {
    private Long playerId;
    private String playerName;
    private Double predictedPoints;
    private Double confidence; // 0-1 confidence score
    private String reasoning; // Brief explanation
    
    public PlayerPredictionDTO() {}
    
    public PlayerPredictionDTO(Long playerId, String playerName, Double predictedPoints, Double confidence, String reasoning) {
        this.playerId = playerId;
        this.playerName = playerName;
        this.predictedPoints = predictedPoints;
        this.confidence = confidence;
        this.reasoning = reasoning;
    }
    
    // Getters and setters
    public Long getPlayerId() {
        return playerId;
    }
    
    public void setPlayerId(Long playerId) {
        this.playerId = playerId;
    }
    
    public String getPlayerName() {
        return playerName;
    }
    
    public void setPlayerName(String playerName) {
        this.playerName = playerName;
    }
    
    public Double getPredictedPoints() {
        return predictedPoints;
    }
    
    public void setPredictedPoints(Double predictedPoints) {
        this.predictedPoints = predictedPoints;
    }
    
    public Double getConfidence() {
        return confidence;
    }
    
    public void setConfidence(Double confidence) {
        this.confidence = confidence;
    }
    
    public String getReasoning() {
        return reasoning;
    }
    
    public void setReasoning(String reasoning) {
        this.reasoning = reasoning;
    }
}
