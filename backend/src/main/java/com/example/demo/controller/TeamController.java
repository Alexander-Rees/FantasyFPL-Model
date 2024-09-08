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

    @GetMapping
    public Team getTeam(@RequestParam Long userId) {
        return teamService.getTeamByUserId(userId);
    }

    // Update to only accept playerId instead of full Player object
    @PostMapping
    public Team addPlayerToTeam(@RequestParam Long userId, @RequestParam Long playerId) {
        return teamService.addPlayerToTeam(userId, playerId);
    }

    @DeleteMapping("/{playerId}")
    public Team removePlayerFromTeam(@RequestParam Long userId, @PathVariable Long playerId) {
        return teamService.removePlayerFromTeam(userId, playerId);
    }

    @PostMapping("/create")
    public Team createTeam(@RequestBody CreateTeamDTO createTeamDTO) {
        return teamService.createTeam(createTeamDTO);
    }

    @GetMapping("/optimal_team")
    public String getOptimalTeam() {
        return teamService.getOptimalTeam();
    }

    @GetMapping("/top_players")
    public String getTopPlayers() {
        return teamService.getTopPlayers();
    }
}
