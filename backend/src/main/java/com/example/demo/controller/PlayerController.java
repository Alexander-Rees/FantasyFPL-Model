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

    // Endpoint to fetch all player data from database
    @GetMapping
    public List<PlayerDTO> getPlayerData() {
        return playerDataService.getAllPlayers();
    }
}
