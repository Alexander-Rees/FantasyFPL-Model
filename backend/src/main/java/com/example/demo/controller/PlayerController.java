package com.example.demo.controller;

import com.example.demo.dto.PlayerDTO;
import com.example.demo.service.PlayerDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/players")
public class PlayerController {

    @Autowired
    private PlayerDataService playerDataService;

    // Endpoint to fetch player data with basic pagination and filters
    @GetMapping
    public List<PlayerDTO> getPlayerData(
            @RequestParam(name = "page", required = false, defaultValue = "0") int page,
            @RequestParam(name = "size", required = false, defaultValue = "50") int size,
            @RequestParam(name = "team", required = false) String team,
            @RequestParam(name = "position", required = false) String position,
            @RequestParam(name = "gw", required = false) Integer gw
    ) {
        List<PlayerDTO> players = playerDataService.getAllPlayers();
        if (team != null && !team.isEmpty()) {
            players = players.stream().filter(p -> team.equalsIgnoreCase(p.getTeam())).toList();
        }
        if (position != null && !position.isEmpty()) {
            players = players.stream().filter(p -> position.equalsIgnoreCase(p.getPosition())).toList();
        }
        int from = Math.max(0, Math.min(page * size, players.size()));
        int to = Math.max(0, Math.min(from + size, players.size()));
        return players.subList(from, to);
    }
}
