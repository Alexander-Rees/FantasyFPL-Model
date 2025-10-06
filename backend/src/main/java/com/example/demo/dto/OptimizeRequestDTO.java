package com.example.demo.dto;

import java.util.List;

public class OptimizeRequestDTO {
    private Long teamId;
    private Long entryId;
    private Double budget;
    private Integer freeTransfers;
    private List<Long> lockedPlayers;
    private List<Long> avoidPlayers;
    private String formation;

    // Constructors
    public OptimizeRequestDTO() {}

    public OptimizeRequestDTO(Long teamId, Long entryId, Double budget, Integer freeTransfers, 
                             List<Long> lockedPlayers, List<Long> avoidPlayers, String formation) {
        this.teamId = teamId;
        this.entryId = entryId;
        this.budget = budget;
        this.freeTransfers = freeTransfers;
        this.lockedPlayers = lockedPlayers;
        this.avoidPlayers = avoidPlayers;
        this.formation = formation;
    }

    // Getters and setters
    public Long getTeamId() {
        return teamId;
    }

    public void setTeamId(Long teamId) {
        this.teamId = teamId;
    }

    public Long getEntryId() {
        return entryId;
    }

    public void setEntryId(Long entryId) {
        this.entryId = entryId;
    }

    public Double getBudget() {
        return budget;
    }

    public void setBudget(Double budget) {
        this.budget = budget;
    }

    public Integer getFreeTransfers() {
        return freeTransfers;
    }

    public void setFreeTransfers(Integer freeTransfers) {
        this.freeTransfers = freeTransfers;
    }

    public List<Long> getLockedPlayers() {
        return lockedPlayers;
    }

    public void setLockedPlayers(List<Long> lockedPlayers) {
        this.lockedPlayers = lockedPlayers;
    }

    public List<Long> getAvoidPlayers() {
        return avoidPlayers;
    }

    public void setAvoidPlayers(List<Long> avoidPlayers) {
        this.avoidPlayers = avoidPlayers;
    }

    public String getFormation() {
        return formation;
    }

    public void setFormation(String formation) {
        this.formation = formation;
    }
}