package com.example.demo.service;

import com.example.demo.dto.PlayerResponseDTO;
import com.example.demo.dto.ResponseDTO;
import com.example.demo.dto.PlayerDTO;
import com.example.demo.dto.PlayerStatisticsDTO;
import com.example.demo.model.Player;
import com.example.demo.repository.PlayerRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
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

    private static final String API_URL = "https://v3.football.api-sports.io/players?league=79&season=2023";

    @EventListener(ApplicationReadyEvent.class)
    public void fetchAndPopulatePlayerData() {
        RestTemplate restTemplate = new RestTemplate();

        HttpHeaders headers = new HttpHeaders();
        headers.set("x-apisports-key", "7867eeb4f98e8bf594ad74d0d1e3fd05"); // Replace with your actual API key
        HttpEntity<String> entity = new HttpEntity<>(headers);

        ResponseEntity<String> response = restTemplate.exchange(API_URL, HttpMethod.GET, entity, String.class);

        if (response.getBody() != null) {
            System.out.println("Raw API Response: " + response.getBody());

            ObjectMapper objectMapper = new ObjectMapper();
            try {
                PlayerResponseDTO playerResponse = objectMapper.readValue(response.getBody(), PlayerResponseDTO.class);

                if (playerResponse != null && playerResponse.getResponse() != null) {
                    List<ResponseDTO> players = playerResponse.getResponse();
                    System.out.println("Number of players fetched: " + players.size());

                    for (ResponseDTO responseDTO : players) {
                        PlayerDTO playerDTO = responseDTO.getPlayer();
                        if (responseDTO.getStatistics() != null && !responseDTO.getStatistics().isEmpty()) {
                            PlayerStatisticsDTO statistics = responseDTO.getStatistics().get(0);
                            if (statistics.getGames() != null /*
                                                               * && statistics.getGames().getAppearances() != null &&
                                                               * statistics.getGames().getAppearances() > 0
                                                               */) {
                                Player player = new Player(
                                        playerDTO.getId(),
                                        playerDTO.getName(),
                                        new Random().nextInt(100), // Assign random points
                                        statistics.getGames().getPosition(),
                                        "Bundesliga 2" // Set the league name manually or get from response if available
                                );
                                System.out.println("Saving player: " + player.getName());
                                playerRepository.save(player);
                            }
                        }
                    }
                    System.out.println("Player data fetch and save completed.");
                } else {
                    System.out.println("No player data available in the response.");
                }
            } catch (Exception e) {
                System.out.println("Error parsing JSON: " + e.getMessage());
            }
        } else {
            System.out.println("API response body is null.");
        }
    }
}
