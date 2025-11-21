package com.example.demo.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.Table;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonBackReference;

@Entity
@Table(name = "player")
public class Player {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String position;
    private String team;
    private Long fplId; // FPL API player ID

    // Default values for numeric fields
    private double value = 0.0;
    private int totalPoints = 0;
    private int weeklyPoints = 0;

    @ManyToMany(mappedBy = "players")
    @JsonBackReference
    private List<Team> teams;

    // Default constructor
    public Player() {
    }

    // Constructor with parameters
    public Player(Long id, String name, String position, String team, double value, int totalPoints, int weeklyPoints) {
        this.id = id;
        this.name = name;
        this.position = position;
        this.team = team;
        this.value = value;
        this.totalPoints = totalPoints;
        this.weeklyPoints = weeklyPoints;
    }

    public Player(Long id, String name, String position, String team, Long fplId, double value, int totalPoints,
            int weeklyPoints) {
        this.id = id;
        this.name = name;
        this.position = position;
        this.team = team;
        this.fplId = fplId;
        this.value = value;
        this.totalPoints = totalPoints;
        this.weeklyPoints = weeklyPoints;
    }

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

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }

    public String getTeam() {
        return team;
    }

    public void setTeam(String team) {
        this.team = team;
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

    public List<Team> getTeams() {
        return teams;
    }

    public void setTeams(List<Team> teams) {
        this.teams = teams;
    }

    public Long getFplId() {
        return fplId;
    }

    public void setFplId(Long fplId) {
        this.fplId = fplId;
    }

    // Predicted Points
    private double predictedPoints = 0.0;

    public double getPredictedPoints() {
        return predictedPoints;
    }

    public void setPredictedPoints(double predictedPoints) {
        this.predictedPoints = predictedPoints;
    }
}
