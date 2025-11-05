package com.example.demo.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import java.util.List;

public class OptimizeRequestDTO {
    @NotNull
    private Long userId;

    @Min(0)
    private Double budget;

    private Integer freeTransfers;

    private List<Long> lockedPlayers;

    private List<Long> avoidPlayers;

    private String formation;

    private Integer gw;

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public Double getBudget() { return budget; }
    public void setBudget(Double budget) { this.budget = budget; }

    public Integer getFreeTransfers() { return freeTransfers; }
    public void setFreeTransfers(Integer freeTransfers) { this.freeTransfers = freeTransfers; }

    public List<Long> getLockedPlayers() { return lockedPlayers; }
    public void setLockedPlayers(List<Long> lockedPlayers) { this.lockedPlayers = lockedPlayers; }

    public List<Long> getAvoidPlayers() { return avoidPlayers; }
    public void setAvoidPlayers(List<Long> avoidPlayers) { this.avoidPlayers = avoidPlayers; }

    public String getFormation() { return formation; }
    public void setFormation(String formation) { this.formation = formation; }

    public Integer getGw() { return gw; }
    public void setGw(Integer gw) { this.gw = gw; }
}