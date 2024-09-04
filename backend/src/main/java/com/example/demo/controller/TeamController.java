package com.example.demo.controller;

import com.example.demo.dto.CreateTeamDTO;
import com.example.demo.model.Player;
import com.example.demo.model.Team;
import com.example.demo.service.TeamService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/team")
public class TeamController {
    @Autowired
    private TeamService teamService;

    // Existing Endpoints

    @GetMapping
    public Team getTeam(@RequestParam Long userId) {
        return teamService.getTeamByUserId(userId);
    }

    @PostMapping
    public Team addPlayerToTeam(@RequestParam Long userId, @RequestBody Player player) {
        return teamService.addPlayerToTeam(userId, player);
    }

    @DeleteMapping("/{playerId}")
    public Team removePlayerFromTeam(@RequestParam Long userId, @PathVariable Long playerId) {
        return teamService.removePlayerFromTeam(userId, playerId);
    }

    @PostMapping("/create")
    public Team createTeam(@RequestBody CreateTeamDTO createTeamDTO) {
        return teamService.createTeam(createTeamDTO);
    }

    // New Endpoints to Integrate with Flask API

    // Endpoint to get the optimal team from the Flask API
    @GetMapping("/optimal_team")
    public String getOptimalTeam() {
        return teamService.getOptimalTeam();
    }

    // Endpoint to get top players by position from the Flask API
    @GetMapping("/top_players")
    public String getTopPlayers() {
        return teamService.getTopPlayers();
    }
}
