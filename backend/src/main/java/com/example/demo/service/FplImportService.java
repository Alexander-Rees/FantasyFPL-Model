package com.example.demo.service;

import com.example.demo.dto.PlayerDTO;
import com.example.demo.model.Player;
import com.example.demo.model.Team;
import com.example.demo.model.User;
import com.example.demo.repository.PlayerRepository;
import com.example.demo.repository.TeamRepository;
import com.example.demo.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.stream.Collectors;
import java.util.Optional;

@Service
public class FplImportService {

    @Autowired
    private PlayerRepository playerRepository;

    @Autowired
    private TeamRepository teamRepository;

    @Autowired
    private UserRepository userRepository;

    private final RestTemplate restTemplate;
    private final String FPL_BASE_URL = "https://fantasy.premierleague.com/api";
    
    public FplImportService() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(10000); // 10 seconds
        factory.setReadTimeout(10000); // 10 seconds
        this.restTemplate = new RestTemplate(factory);
    }

    public Team importTeamFromFpl(Long userId, Long entryId) {
        try {
            System.out.println("Starting FPL import for user " + userId + ", entry " + entryId);
            
            // Try to get the most recent team data by checking multiple gameweeks
            // Start from a high gameweek and work backwards until we find data
            Map<String, Object> teamData = null;
            Integer gameweekUsed = null;
            
            // First, try to get the current gameweek from the API
            Integer currentGameweek = getCurrentGameweek();
            System.out.println("API reports current gameweek: " + currentGameweek);
            
            // Force try gameweek 7 first since we know that's the most recent
            System.out.println("Trying gameweek 7 first (most recent known)...");
            try {
                String picksUrl = String.format("%s/entry/%d/event/%d/picks/", FPL_BASE_URL, entryId, 7);
                System.out.println("Trying gameweek 7: " + picksUrl);
                
                ResponseEntity<Map> response = restTemplate.getForEntity(picksUrl, Map.class);
                
                if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                    Map<String, Object> data = response.getBody();
                    List<Map<String, Object>> picks = (List<Map<String, Object>>) data.get("picks");
                    
                    if (picks != null && !picks.isEmpty()) {
                        teamData = data;
                        gameweekUsed = 7;
                        System.out.println("Found team data for gameweek 7 with " + picks.size() + " players");
                    }
                }
            } catch (Exception e) {
                System.out.println("Gameweek 7 failed: " + e.getMessage());
            }
            
            // If gameweek 7 didn't work, try current gameweek first, then work backwards
            if (teamData == null) {
                System.out.println("Gameweek 7 failed, trying current gameweek and working backwards...");
                for (int gw = currentGameweek; gw >= 1; gw--) {
                    try {
                        String picksUrl = String.format("%s/entry/%d/event/%d/picks/", FPL_BASE_URL, entryId, gw);
                        System.out.println("Trying gameweek " + gw + ": " + picksUrl);
                        
                        ResponseEntity<Map> response = restTemplate.getForEntity(picksUrl, Map.class);
                        
                        if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                            Map<String, Object> data = response.getBody();
                            List<Map<String, Object>> picks = (List<Map<String, Object>>) data.get("picks");
                            
                            if (picks != null && !picks.isEmpty()) {
                                teamData = data;
                                gameweekUsed = gw;
                                System.out.println("Found team data for gameweek " + gw + " with " + picks.size() + " players");
                                break;
                            }
                        }
                    } catch (Exception e) {
                        System.out.println("Gameweek " + gw + " failed: " + e.getMessage());
                        continue;
                    }
                }
            }
            
            // If we still haven't found data, try from gameweek 20 down to current+1
            if (teamData == null) {
                System.out.println("No data found from current gameweek down, trying higher gameweeks...");
                for (int gw = 20; gw > currentGameweek; gw--) {
                    try {
                        String picksUrl = String.format("%s/entry/%d/event/%d/picks/", FPL_BASE_URL, entryId, gw);
                        System.out.println("Trying higher gameweek " + gw + ": " + picksUrl);
                        
                        ResponseEntity<Map> response = restTemplate.getForEntity(picksUrl, Map.class);
                        
                        if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                            Map<String, Object> data = response.getBody();
                            List<Map<String, Object>> picks = (List<Map<String, Object>>) data.get("picks");
                            
                            if (picks != null && !picks.isEmpty()) {
                                teamData = data;
                                gameweekUsed = gw;
                                System.out.println("Found team data for gameweek " + gw + " with " + picks.size() + " players");
                                break;
                            }
                        }
                    } catch (Exception e) {
                        System.out.println("Gameweek " + gw + " failed: " + e.getMessage());
                        continue;
                    }
                }
            }
            
            if (teamData == null) {
                throw new RuntimeException("Could not find team data for any gameweek");
            }
            
            // Extract picks
            List<Map<String, Object>> picks = (List<Map<String, Object>>) teamData.get("picks");
            System.out.println("Using team data from gameweek " + gameweekUsed + " with " + picks.size() + " players");
            
            // Get user first
            System.out.println("Looking for user with ID: " + userId);
            Optional<User> userOpt = userRepository.findById(userId);
            if (!userOpt.isPresent()) {
                System.out.println("User not found in database. Available users:");
                userRepository.findAll().forEach(u -> System.out.println("  - User ID: " + u.getId() + ", Email: " + u.getEmail()));
                throw new RuntimeException("User not found with ID: " + userId + ". Please register or log in first.");
            }
            User user = userOpt.get();
            System.out.println("Found user: " + user.getEmail() + " (ID: " + user.getId() + ")");
            
            // Get or create team for user
            Team team = teamRepository.findByUserId(userId);
            if (team == null) {
                team = new Team();
                team.setUser(user);
                team.setName("FPL Team " + entryId + " (GW" + gameweekUsed + ")");
                team.setBudget(100.0);
                team = teamRepository.save(team);
                System.out.println("Created new team: " + team.getId());
            } else {
                System.out.println("Found existing team: " + team.getId());
                // Clear existing players
                team.getPlayers().clear();
            }
            
            // Process each pick and add players to team
            List<Player> teamPlayers = new ArrayList<>();
            for (Map<String, Object> pick : picks) {
                Integer fplPlayerId = (Integer) pick.get("element");
                Optional<Player> playerOpt = playerRepository.findByFplId(fplPlayerId.longValue());
                
                if (playerOpt.isPresent()) {
                    teamPlayers.add(playerOpt.get());
                    System.out.println("Added player: " + playerOpt.get().getName() + " (FPL ID: " + fplPlayerId + ")");
                } else {
                    System.out.println("Warning: FPL player ID " + fplPlayerId + " not found in database");
                }
            }
            
            team.setPlayers(teamPlayers);
            
            // Calculate remaining budget
            double totalValue = teamPlayers.stream()
                .mapToDouble(Player::getValue)
                .sum();
            team.setBudget(100.0 - totalValue);
            
            team = teamRepository.save(team);
            System.out.println("Team saved with " + team.getPlayers().size() + " players from gameweek " + gameweekUsed);
            
            return team;
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to import team from FPL: " + e.getMessage(), e);
        }
    }
    
    private Integer getCurrentGameweek() {
        try {
            String bootstrapUrl = FPL_BASE_URL + "/bootstrap-static/";
            ResponseEntity<Map> response = restTemplate.getForEntity(bootstrapUrl, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> data = response.getBody();
                Map<String, Object> currentEvent = (Map<String, Object>) data.get("current-event");
                if (currentEvent != null) {
                    Integer gameweek = (Integer) currentEvent.get("id");
                    System.out.println("Current gameweek from API: " + gameweek);
                    return gameweek;
                }
            }
        } catch (Exception e) {
            System.out.println("Warning: Could not fetch current gameweek: " + e.getMessage());
        }
        
        // If we can't get it from API, try to determine by testing recent gameweeks
        System.out.println("API failed, trying to determine current gameweek by testing recent weeks...");
        for (int gw = 10; gw >= 1; gw--) {
            try {
                String testUrl = String.format("%s/entry/1/event/%d/picks/", FPL_BASE_URL, gw);
                ResponseEntity<Map> testResponse = restTemplate.getForEntity(testUrl, Map.class);
                if (testResponse.getStatusCode().is2xxSuccessful() && testResponse.getBody() != null) {
                    System.out.println("Found valid gameweek: " + gw);
                    return gw;
                }
            } catch (Exception e) {
                continue;
            }
        }
        
        return 7; // Default fallback - we know gameweek 7 exists
    }
    
    public List<PlayerDTO> getTeamPlayers(Long userId) {
        Team team = teamRepository.findByUserId(userId);
        if (team == null) {
            return new ArrayList<>();
        }
        
        return team.getPlayers().stream()
            .map(this::convertToDTO)
            .collect(Collectors.toList());
    }
    
    private PlayerDTO convertToDTO(Player player) {
        PlayerDTO dto = new PlayerDTO();
        dto.setId(player.getId());
        dto.setName(player.getName());
        dto.setPosition(player.getPosition());
        dto.setTeam(player.getTeam());
        dto.setValue(player.getValue());
        dto.setTotalPoints(player.getTotalPoints());
        dto.setWeeklyPoints(player.getWeeklyPoints());
        return dto;
    }
}
