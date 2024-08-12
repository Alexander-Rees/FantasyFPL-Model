package com.example.demo.controller;

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

    @PostMapping
    public Team addPlayerToTeam(@RequestParam Long userId, @RequestBody Player player) {
        return teamService.addPlayerToTeam(userId, player);
    }

    @DeleteMapping("/{playerId}")
    public Team removePlayerFromTeam(@RequestParam Long userId, @PathVariable Long playerId) {
        return teamService.removePlayerFromTeam(userId, playerId);
    }
}
