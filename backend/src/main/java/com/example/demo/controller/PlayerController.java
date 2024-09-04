package com.example.demo.controller;

import com.example.demo.dto.PlayerDTO;
import com.example.demo.service.PlayerDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/players")
public class PlayerController {

    @Autowired
    private PlayerDataService playerDataService;

    // Endpoint to fetch weekly player data for a specific gameweek
    @GetMapping("/weekly/{gameweek}")
    public List<PlayerDTO> getWeeklyPlayerData(@PathVariable int gameweek) {
        return playerDataService.fetchWeeklyPlayerData(gameweek);
    }

    // Endpoint to fetch total player data (across all gameweeks)
    @GetMapping("/total")
    public List<PlayerDTO> getTotalPlayerData() {
        return playerDataService.fetchTotalPlayerData();
    }
}
