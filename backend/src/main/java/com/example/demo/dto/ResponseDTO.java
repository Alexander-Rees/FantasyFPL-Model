package com.example.demo.dto;

import java.util.List;

public class ResponseDTO {
    private PlayerDTO player;
    private List<PlayerStatisticsDTO> statistics;

    // Getters and setters
    public PlayerDTO getPlayer() {
        return player;
    }

    public void setPlayer(PlayerDTO player) {
        this.player = player;
    }

    public List<PlayerStatisticsDTO> getStatistics() {
        return statistics;
    }

    public void setStatistics(List<PlayerStatisticsDTO> statistics) {
        this.statistics = statistics;
    }
}
