package com.example.demo.controller;

import com.example.demo.dto.CreateTeamDTO;
import com.example.demo.dto.FplImportRequestDTO;
import com.example.demo.dto.OptimizeRequestDTO;
import com.example.demo.dto.OptimizeResponseDTO;
import com.example.demo.dto.PlayerDTO;
import com.example.demo.model.Player;
import com.example.demo.model.Team;
import com.example.demo.service.FplImportService;
import com.example.demo.service.TeamOptimizationService;
import com.example.demo.service.TeamService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/team")
public class TeamController {

    @Autowired
    private TeamService teamService;
    
    @Autowired
    private FplImportService fplImportService;
    
    @Autowired
    private TeamOptimizationService teamOptimizationService;

    @GetMapping
    public Team getTeam(@RequestParam Long userId) {
        return teamService.getTeamByUserId(userId);
    }

    // Update to only accept playerId instead of full Player object
    @PostMapping
    public ResponseEntity<Team> addPlayerToTeam(@RequestParam Long userId, @RequestParam Long playerId) {
        try {
            System.out.println("Adding player with ID: " + playerId + " to user with ID: " + userId);
            Team updatedTeam = teamService.addPlayerToTeam(userId, playerId);
            System.out.println("Player added successfully. Updated team: " + updatedTeam);
            return ResponseEntity.ok(updatedTeam);
        } catch (Exception e) {
            System.err.println("Error occurred: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(null);
        }
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
    
    // FPL Import endpoints
    @PostMapping("/import/fpl-entry")
    public ResponseEntity<Team> importFromFpl(@RequestParam Long userId, @RequestBody FplImportRequestDTO request) {
        try {
            Team team = fplImportService.importTeamFromFpl(userId, request.getEntryId());
            return ResponseEntity.ok(team);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(null);
        }
    }
    
    @GetMapping("/players")
    public ResponseEntity<List<PlayerDTO>> getTeamPlayers(@RequestParam Long userId) {
        try {
            List<PlayerDTO> players = fplImportService.getTeamPlayers(userId);
            return ResponseEntity.ok(players);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(null);
        }
    }
    
    // Team optimization endpoint
    @PostMapping("/optimize")
    public ResponseEntity<OptimizeResponseDTO> optimizeTeam(@RequestParam Long userId, @RequestBody OptimizeRequestDTO request) {
        try {
            System.out.println("Optimization request received for user: " + userId);
            OptimizeResponseDTO response = teamOptimizationService.optimizeTeam(userId, request);
            System.out.println("Optimization completed successfully");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.err.println("Optimization error: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(null);
        }
    }
    
    // Simple test endpoint
    @GetMapping("/test")
    public ResponseEntity<String> test() {
        return ResponseEntity.ok("Test endpoint working");
    }
}
