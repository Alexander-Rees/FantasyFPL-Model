package com.example.demo.service;

import com.example.demo.dto.*;
import com.example.demo.model.Player;
import com.example.demo.model.Team;
import com.example.demo.model.User;
import com.example.demo.repository.PlayerRepository;
import com.example.demo.repository.TeamRepository;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import io.github.resilience4j.bulkhead.annotation.Bulkhead;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
public class TeamOptimizationService {

    @Autowired
    private TeamRepository teamRepository;

    @Autowired
    private PlayerRepository playerRepository;

    @Autowired
    private PlayerDataService playerDataService;

    @Autowired(required = false)
    private StringRedisTemplate redisTemplate;

    @Value("${flask.api.url:http://localhost:5001}")
    private String flaskApiUrl;

    private final RestTemplate restTemplate;

    public TeamOptimizationService() {
        this.restTemplate = new RestTemplate();
        // Configure timeouts
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000); // 5 seconds
        factory.setReadTimeout(10000); // 10 seconds
        this.restTemplate.setRequestFactory(factory);
    }

    public OptimizeResponseDTO optimizeTeam(Long userId, OptimizeRequestDTO request) {
        // Get user's current team
        Team currentTeam = teamRepository.findByUserId(userId);
        if (currentTeam == null) {
            // Create a basic team for testing if none exists
            currentTeam = new Team();
            User user = new User();
            user.setId(userId);
            currentTeam.setUser(user);
            currentTeam.setName("Default Team");
            currentTeam.setPlayers(new ArrayList<>());
        }

        try {
            // Get all players for the optimization pool
            List<Player> allPlayers = playerRepository.findAll();
            List<PlayerDTO> playerPool = allPlayers.stream()
                .map(playerDataService::convertToDTO)
                .collect(Collectors.toList());

            // Get current team players
            List<PlayerDTO> currentTeamPlayers = currentTeam.getPlayers().stream()
                .map(playerDataService::convertToDTO)
                .collect(Collectors.toList());

            System.out.println("Player pool size: " + playerPool.size());
            System.out.println("Current team size: " + currentTeamPlayers.size());

            // Prepare request for Flask ML API
            Map<String, Object> flaskRequest = new HashMap<>();
            flaskRequest.put("players", playerPool);
            flaskRequest.put("current_team", currentTeamPlayers);
            flaskRequest.put("budget", request.getBudget() != null ? request.getBudget() : 100.0);
            flaskRequest.put("free_transfers", request.getFreeTransfers() != null ? request.getFreeTransfers() : 1);
            flaskRequest.put("locked_players", request.getLockedPlayers() != null ? request.getLockedPlayers() : new ArrayList<>());
            flaskRequest.put("avoid_players", request.getAvoidPlayers() != null ? request.getAvoidPlayers() : new ArrayList<>());
            flaskRequest.put("formation", request.getFormation() != null ? request.getFormation() : "3-4-3");

            System.out.println("Calling Flask API at: " + flaskApiUrl + "/_ml/optimize");

            // Call Flask ML API with resilience patterns
            Map<String, Object> flaskResponse = callFlaskOptimization(flaskRequest);
            return parseFlaskResponse(flaskResponse);

        } catch (Exception e) {
            System.out.println("Flask API call failed, using fallback: " + e.getMessage());
            e.printStackTrace();
            // Fallback to basic optimization if Flask is unavailable
            return createFallbackOptimization(currentTeam, request);
        }
    }

    @CircuitBreaker(name = "flaskMl", fallbackMethod = "flaskFallback")
    @Retry(name = "flaskMl")
    @Bulkhead(name = "flaskMl")
    private Map<String, Object> callFlaskOptimization(Map<String, Object> flaskRequest) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        // Service-to-service auth header
        String internalToken = System.getProperty("INTERNAL_API_TOKEN",
                System.getenv().getOrDefault("INTERNAL_API_TOKEN", "dev-internal-token"));
        headers.add("X-Internal-Token", internalToken);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(flaskRequest, headers);

        String optimizeUrl = flaskApiUrl + "/_ml/optimize";
        ResponseEntity<Map> response = restTemplate.postForEntity(optimizeUrl, entity, Map.class);

        System.out.println("Flask API response status: " + response.getStatusCode());
        System.out.println("Flask API response body: " + response.getBody());

        if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
            return response.getBody();
        } else {
            throw new RuntimeException("Flask API returned error: " + response.getStatusCode());
        }
    }

    private Map<String, Object> flaskFallback(Map<String, Object> flaskRequest, Exception e) {
        System.out.println("Circuit breaker fallback triggered: " + e.getMessage());
        throw new RuntimeException("Flask service unavailable", e);
    }

    private OptimizeResponseDTO parseFlaskResponse(Map<String, Object> response) {
        System.out.println("Parsing Flask response: " + response);
        
        // Parse the response from Flask ML API with null checks
        List<Map<String, Object>> optimalTeamData = (List<Map<String, Object>>) response.get("optimal_team");
        List<Map<String, Object>> benchData = (List<Map<String, Object>>) response.get("bench");
        Map<String, Object> captainData = (Map<String, Object>) response.get("captain");
        Map<String, Object> viceCaptainData = (Map<String, Object>) response.get("vice_captain");
        List<Map<String, Object>> transfersData = (List<Map<String, Object>>) response.get("transfers");

        List<PlayerDTO> optimalTeam = optimalTeamData != null ? convertToPlayerDTOs(optimalTeamData) : new ArrayList<>();
        List<PlayerDTO> bench = benchData != null ? convertToPlayerDTOs(benchData) : new ArrayList<>();
        PlayerDTO captain = captainData != null ? convertToPlayerDTO(captainData) : null;
        PlayerDTO viceCaptain = viceCaptainData != null ? convertToPlayerDTO(viceCaptainData) : null;
        List<TransferDTO> transfers = transfersData != null ? convertToTransferDTOs(transfersData) : new ArrayList<>();

        Double totalValue = response.get("total_value") != null ? ((Number) response.get("total_value")).doubleValue() : 0.0;
        Integer totalPoints = response.get("total_points") != null ? ((Number) response.get("total_points")).intValue() : 0;
        String formation = (String) response.get("formation");

        System.out.println("Parsed response - optimalTeam: " + optimalTeam.size() + ", transfers: " + transfers.size());
        
        return new OptimizeResponseDTO(optimalTeam, bench, captain, viceCaptain, 
                                     transfers, totalValue, totalPoints, formation);
    }

    private List<PlayerDTO> convertToPlayerDTOs(List<Map<String, Object>> playerData) {
        if (playerData == null) return new ArrayList<>();
        
        return playerData.stream()
            .map(this::convertToPlayerDTO)
            .filter(Objects::nonNull)
            .collect(Collectors.toList());
    }

    private PlayerDTO convertToPlayerDTO(Map<String, Object> playerData) {
        if (playerData == null) return null;
        
        PlayerDTO dto = new PlayerDTO();
        dto.setId(((Number) playerData.get("id")).longValue());
        dto.setName((String) playerData.get("name"));
        dto.setTeam((String) playerData.get("team"));
        dto.setPosition((String) playerData.get("position"));
        dto.setValue(((Number) playerData.get("value")).doubleValue());
        dto.setTotalPoints(((Number) playerData.get("total_points")).intValue());
        dto.setWeeklyPoints(((Number) playerData.get("weekly_points")).intValue());
        dto.setFplId(((Number) playerData.get("fplId")).longValue());
        return dto;
    }

    private List<TransferDTO> convertToTransferDTOs(List<Map<String, Object>> transfersData) {
        if (transfersData == null) return new ArrayList<>();
        
        return transfersData.stream()
            .map(this::convertToTransferDTO)
            .filter(Objects::nonNull)
            .collect(Collectors.toList());
    }

    private TransferDTO convertToTransferDTO(Map<String, Object> transferData) {
        if (transferData == null) return null;
        
        PlayerDTO playerOut = convertToPlayerDTO((Map<String, Object>) transferData.get("player_out"));
        PlayerDTO playerIn = convertToPlayerDTO((Map<String, Object>) transferData.get("player_in"));
        Double cost = ((Number) transferData.get("cost")).doubleValue();
        String reason = (String) transferData.get("reason");
        
        return new TransferDTO(playerOut, playerIn, cost, reason);
    }

    private OptimizeResponseDTO createFallbackOptimization(Team currentTeam, OptimizeRequestDTO request) {
        // Get all players for the optimization pool
        List<Player> allPlayers = playerRepository.findAll();
        List<PlayerDTO> playerPool = allPlayers.stream()
            .map(playerDataService::convertToDTO)
            .collect(Collectors.toList());

        // Sort players by total points (descending) and value (ascending)
        playerPool.sort(Comparator
            .comparing(PlayerDTO::getTotalPoints).reversed()
            .thenComparing(PlayerDTO::getValue));

        List<PlayerDTO> optimalTeam = new ArrayList<>();
        List<PlayerDTO> bench = new ArrayList<>();
        double currentBudget = request.getBudget() != null ? request.getBudget() : 100.0;
        int freeTransfers = request.getFreeTransfers() != null ? request.getFreeTransfers() : 1;
        String formation = request.getFormation() != null ? request.getFormation() : "3-4-3";

        Map<String, Integer> positionLimits = new HashMap<>();
        switch (formation) {
            case "3-4-3":
                positionLimits.put("GK", 1); positionLimits.put("DEF", 3); positionLimits.put("MID", 4); positionLimits.put("FWD", 3);
                break;
            case "3-5-2":
                positionLimits.put("GK", 1); positionLimits.put("DEF", 3); positionLimits.put("MID", 5); positionLimits.put("FWD", 2);
                break;
            case "4-4-2":
                positionLimits.put("GK", 1); positionLimits.put("DEF", 4); positionLimits.put("MID", 4); positionLimits.put("FWD", 2);
                break;
            case "4-3-3":
                positionLimits.put("GK", 1); positionLimits.put("DEF", 4); positionLimits.put("MID", 3); positionLimits.put("FWD", 3);
                break;
            case "5-4-1":
                positionLimits.put("GK", 1); positionLimits.put("DEF", 5); positionLimits.put("MID", 4); positionLimits.put("FWD", 1);
                break;
            default: // Default to 3-4-3
                positionLimits.put("GK", 1); positionLimits.put("DEF", 3); positionLimits.put("MID", 4); positionLimits.put("FWD", 3);
                break;
        }

        Map<String, Integer> selectedPositions = new HashMap<>();
        for (String pos : positionLimits.keySet()) {
            selectedPositions.put(pos, 0);
        }

        Set<Long> selectedPlayerIds = new HashSet<>();
        for (PlayerDTO player : playerPool) {
            String position = player.getPosition();
            if (positionLimits.containsKey(position) && selectedPositions.get(position) < positionLimits.get(position) && currentBudget >= player.getValue()) {
                optimalTeam.add(player);
                selectedPlayerIds.add(player.getId());
                selectedPositions.put(position, selectedPositions.get(position) + 1);
                currentBudget -= player.getValue();
            }
            if (optimalTeam.size() == 11) break;
        }

        // Fill bench with remaining top players
        for (PlayerDTO player : playerPool) {
            if (!selectedPlayerIds.contains(player.getId()) && bench.size() < 4) {
                bench.add(player);
                selectedPlayerIds.add(player.getId());
            }
            if (bench.size() == 4) break;
        }

        // Simple captain/vice-captain selection
        PlayerDTO captain = optimalTeam.isEmpty() ? null : optimalTeam.get(0);
        PlayerDTO viceCaptain = optimalTeam.size() < 2 ? null : optimalTeam.get(1);

        // Simple transfer suggestions (replace lowest scoring current team players with highest scoring available players)
        List<TransferDTO> transfers = new ArrayList<>();
        if (freeTransfers > 0 && currentTeam != null && !currentTeam.getPlayers().isEmpty()) {
            List<PlayerDTO> currentTeamPlayers = currentTeam.getPlayers().stream()
                .map(playerDataService::convertToDTO)
                .sorted(Comparator.comparing(PlayerDTO::getTotalPoints)) // Sort by lowest points
                .collect(Collectors.toList());

            List<PlayerDTO> availablePlayers = playerPool.stream()
                .filter(p -> !selectedPlayerIds.contains(p.getId()))
                .sorted(Comparator.comparing(PlayerDTO::getTotalPoints).reversed()) // Sort by highest points
                .collect(Collectors.toList());

            for (int i = 0; i < Math.min(freeTransfers, currentTeamPlayers.size()); i++) {
                PlayerDTO playerOut = currentTeamPlayers.get(i);
                for (PlayerDTO playerIn : availablePlayers) {
                    if (playerIn.getPosition().equals(playerOut.getPosition()) && playerIn.getValue() <= (currentBudget + playerOut.getValue())) {
                        transfers.add(new TransferDTO(playerOut, playerIn, playerIn.getValue() - playerOut.getValue(), "Fallback transfer suggestion"));
                        currentBudget += (playerOut.getValue() - playerIn.getValue());
                        availablePlayers.remove(playerIn);
                        break;
                    }
                }
            }
        }

        Double totalValue = optimalTeam.stream().mapToDouble(PlayerDTO::getValue).sum();
        Integer totalPoints = optimalTeam.stream().mapToInt(PlayerDTO::getTotalPoints).sum();

        return new OptimizeResponseDTO(optimalTeam, bench, captain, viceCaptain, transfers, totalValue, totalPoints, formation);
    }
}
