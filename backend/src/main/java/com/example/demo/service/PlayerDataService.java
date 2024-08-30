package com.example.demo.service;

import com.example.demo.dto.PlayerResponseDTO;
import com.example.demo.dto.ResponseDTO;
import com.example.demo.dto.PlayerDTO;
import com.example.demo.dto.PlayerStatisticsDTO;
import com.example.demo.model.Player;
import com.example.demo.model.Team;
import com.example.demo.repository.PlayerRepository;
import com.example.demo.repository.TeamRepository;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.transaction.Transactional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.event.EventListener;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.boot.context.event.ApplicationReadyEvent;

import java.util.List;
import java.util.Random;

@Service
public class PlayerDataService {

    @Autowired
    private PlayerRepository playerRepository;

    @Autowired
    private TeamRepository teamRepository;

    private static final String API_URL = "https://v3.football.api-sports.io/players";
    private static final String LEAGUE_ID = "39"; // Premier League ID
    private static final String SEASON = "2024"; // Season 2023

    @Transactional // Ensure this method runs within a transaction
    public void clearPlayerAssociations() {
        List<Team> teams = teamRepository.findAll();
        for (Team team : teams) {
            team.getPlayers().clear(); // Clear the players collection
            teamRepository.save(team);
        }
        System.out.println("All player associations with teams have been cleared.");
    }

    @Transactional
    @EventListener(ApplicationReadyEvent.class)
    public void fetchAndPopulatePlayerData() {
        try {
            clearPlayerAssociations();
            playerRepository.deleteAll();
            System.out.println("All existing players have been deleted.");
            fetchAllPlayers();
        } catch (Exception e) {
            System.err.println("Error during data population: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void fetchAllPlayers() {
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.set("x-apisports-key", "7867eeb4f98e8bf594ad74d0d1e3fd05"); // Replace with your actual API key
        HttpEntity<String> entity = new HttpEntity<>(headers);
        ObjectMapper objectMapper = new ObjectMapper();

        int page = 1;
        boolean hasMorePages = true;

        while (hasMorePages) {
            String url = API_URL + "?league=" + LEAGUE_ID + "&season=" + SEASON + "&page=" + page;

            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, entity, String.class);

            if (response.getBody() != null) {
                System.out.println("Raw API Response for page " + page + ": " + response.getBody());

                try {
                    PlayerResponseDTO playerResponse = objectMapper.readValue(response.getBody(),
                            PlayerResponseDTO.class);

                    if (playerResponse != null && playerResponse.getResponse() != null) {
                        List<ResponseDTO> players = playerResponse.getResponse();
                        System.out.println("Number of players fetched on page " + page + ": " + players.size());

                        for (ResponseDTO responseDTO : players) {
                            PlayerDTO playerDTO = responseDTO.getPlayer();
                            if (responseDTO.getStatistics() != null && !responseDTO.getStatistics().isEmpty()) {
                                PlayerStatisticsDTO statistics = responseDTO.getStatistics().get(0);
                                if (statistics.getGames() != null) {
                                    Player player = new Player(
                                            playerDTO.getId(),
                                            playerDTO.getName(),
                                            new Random().nextInt(100), // Assign random points
                                            statistics.getGames().getPosition(),
                                            "Premier League" // Set the league name manually
                                    );
                                    System.out.println("Saving player: " + player.getName());
                                    playerRepository.save(player);
                                }
                            }
                        }

                        // Check if there are more pages to fetch
                        hasMorePages = players.size() > 0; // If no players returned, we reached the end
                        page++; // Increment page number
                    } else {
                        hasMorePages = false;
                        System.out.println("No more player data available in the response.");
                    }
                } catch (Exception e) {
                    hasMorePages = false;
                    System.out.println("Error parsing JSON: " + e.getMessage());
                }
            } else {
                hasMorePages = false;
                System.out.println("API response body is null.");
            }
        }

        System.out.println("Player data fetch and save completed.");
    }
}
