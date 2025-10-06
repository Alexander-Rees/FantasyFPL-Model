package com.example.demo.dto;

import java.util.List;

public class OptimizeResponseDTO {
    private List<PlayerDTO> optimalTeam;
    private List<PlayerDTO> bench;
    private PlayerDTO captain;
    private PlayerDTO viceCaptain;
    private List<TransferDTO> transfers;
    private Double totalValue;
    private Integer totalPoints;
    private String formation;

    // Constructors
    public OptimizeResponseDTO() {}

    public OptimizeResponseDTO(List<PlayerDTO> optimalTeam, List<PlayerDTO> bench, 
                              PlayerDTO captain, PlayerDTO viceCaptain, 
                              List<TransferDTO> transfers, Double totalValue, 
                              Integer totalPoints, String formation) {
        this.optimalTeam = optimalTeam;
        this.bench = bench;
        this.captain = captain;
        this.viceCaptain = viceCaptain;
        this.transfers = transfers;
        this.totalValue = totalValue;
        this.totalPoints = totalPoints;
        this.formation = formation;
    }

    // Getters and setters
    public List<PlayerDTO> getOptimalTeam() {
        return optimalTeam;
    }

    public void setOptimalTeam(List<PlayerDTO> optimalTeam) {
        this.optimalTeam = optimalTeam;
    }

    public List<PlayerDTO> getBench() {
        return bench;
    }

    public void setBench(List<PlayerDTO> bench) {
        this.bench = bench;
    }

    public PlayerDTO getCaptain() {
        return captain;
    }

    public void setCaptain(PlayerDTO captain) {
        this.captain = captain;
    }

    public PlayerDTO getViceCaptain() {
        return viceCaptain;
    }

    public void setViceCaptain(PlayerDTO viceCaptain) {
        this.viceCaptain = viceCaptain;
    }

    public List<TransferDTO> getTransfers() {
        return transfers;
    }

    public void setTransfers(List<TransferDTO> transfers) {
        this.transfers = transfers;
    }

    public Double getTotalValue() {
        return totalValue;
    }

    public void setTotalValue(Double totalValue) {
        this.totalValue = totalValue;
    }

    public Integer getTotalPoints() {
        return totalPoints;
    }

    public void setTotalPoints(Integer totalPoints) {
        this.totalPoints = totalPoints;
    }

    public String getFormation() {
        return formation;
    }

    public void setFormation(String formation) {
        this.formation = formation;
    }
}