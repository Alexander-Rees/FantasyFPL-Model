package com.example.demo.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class PlayerDTO {
    private Long id;
    private String name;
    private String team;
    private String position; // Ensure consistency with the Player model
    private double value; // Player's current value (cost)

    @JsonProperty("totalPoints")
    private int totalPoints; // Total points for the season

    @JsonProperty("weeklyPoints")
    private int weeklyPoints; // Points for the most recent gameweek

    @JsonProperty("fplId")
    private Long fplId; // Official FPL player ID

    // Getters and setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getTeam() {
        return team;
    }

    public void setTeam(String team) {
        this.team = team;
    }

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }

    public double getValue() {
        return value;
    }

    public void setValue(double value) {
        this.value = value;
    }

    public int getTotalPoints() {
        return totalPoints;
    }

    public void setTotalPoints(int totalPoints) {
        this.totalPoints = totalPoints;
    }

    public int getWeeklyPoints() {
        return weeklyPoints;
    }

    public void setWeeklyPoints(int weeklyPoints) {
        this.weeklyPoints = weeklyPoints;
    }

    public Long getFplId() {
        return fplId;
    }

    public void setFplId(Long fplId) {
        this.fplId = fplId;
    }

    @JsonProperty("predictedPoints")
    private double predictedPoints;

    public double getPredictedPoints() {
        return predictedPoints;
    }

    public void setPredictedPoints(double predictedPoints) {
        this.predictedPoints = predictedPoints;
    }
}
