package com.example.demo.dto;

public class TransferDTO {
    private PlayerDTO playerOut;
    private PlayerDTO playerIn;
    private Double cost;
    private String reason;

    // Constructors
    public TransferDTO() {}

    public TransferDTO(PlayerDTO playerOut, PlayerDTO playerIn, Double cost, String reason) {
        this.playerOut = playerOut;
        this.playerIn = playerIn;
        this.cost = cost;
        this.reason = reason;
    }

    // Getters and setters
    public PlayerDTO getPlayerOut() {
        return playerOut;
    }

    public void setPlayerOut(PlayerDTO playerOut) {
        this.playerOut = playerOut;
    }

    public PlayerDTO getPlayerIn() {
        return playerIn;
    }

    public void setPlayerIn(PlayerDTO playerIn) {
        this.playerIn = playerIn;
    }

    public Double getCost() {
        return cost;
    }

    public void setCost(Double cost) {
        this.cost = cost;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }
}