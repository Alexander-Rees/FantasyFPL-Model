package com.example.demo.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class GamesDTO {
    @JsonProperty("appearences")
    private Integer appearances;

    private String position;

    // Getters and setters
    public Integer getAppearances() {
        return appearances;
    }

    public void setAppearances(Integer appearances) {
        this.appearances = appearances;
    }

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }
}
