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
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/api/v1/team")
public class TeamController {

    @Autowired
    private TeamService teamService;
    
    @Autowired
    private FplImportService fplImportService;
    
    @Autowired
    private TeamOptimizationService teamOptimizationService;

    @Autowired(required = false)
    private StringRedisTemplate redisTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

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
    public ResponseEntity<?> importFromFpl(@RequestParam Long userId, @RequestBody FplImportRequestDTO request) {
        try {
            Team team = fplImportService.importTeamFromFpl(userId, request.getEntryId());
            return ResponseEntity.ok(team);
        } catch (Exception e) {
            System.err.println("Error importing team: " + e.getMessage());
            e.printStackTrace();
            Map<String, String> error = new HashMap<>();
            error.put("message", e.getMessage() != null ? e.getMessage() : "Failed to import team from FPL");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
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
    public ResponseEntity<OptimizeResponseDTO> optimizeTeam(@RequestParam Long userId,
                                                            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
                                                            @RequestBody OptimizeRequestDTO request) {
        try {
            // Idempotency check
            if (idempotencyKey != null && !idempotencyKey.isEmpty() && redisTemplate != null) {
                String cacheKey = "idempotency:" + idempotencyKey;
                String cachedResponse = redisTemplate.opsForValue().get(cacheKey);
                if (cachedResponse != null) {
                    System.out.println("Idempotency key hit: " + idempotencyKey);
                    OptimizeResponseDTO response = objectMapper.readValue(cachedResponse, OptimizeResponseDTO.class);
                    return ResponseEntity.ok(response);
                }
            }

            System.out.println("Optimization request received for user: " + userId);
            OptimizeResponseDTO response = teamOptimizationService.optimizeTeam(userId, request);
            System.out.println("Optimization completed successfully");

            // Cache response with idempotency key (5 minute TTL)
            if (idempotencyKey != null && !idempotencyKey.isEmpty() && redisTemplate != null) {
                try {
                    String cacheKey = "idempotency:" + idempotencyKey;
                    String responseJson = objectMapper.writeValueAsString(response);
                    redisTemplate.opsForValue().set(cacheKey, responseJson, 5, TimeUnit.MINUTES);
                } catch (Exception e) {
                    System.err.println("Failed to cache idempotency response: " + e.getMessage());
                }
            }

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
