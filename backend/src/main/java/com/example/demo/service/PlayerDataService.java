package com.example.demo.service;

import com.example.demo.dto.PlayerDTO;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpMethod;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Arrays;
import java.util.List;

@Service
public class PlayerDataService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final String flaskApiBaseUrl = "http://127.0.0.1:5000"; // Base URL for the Flask API

    // Fetch weekly player data for a specific gameweek
    public List<PlayerDTO> fetchWeeklyPlayerData(int gameweek) {
        String url = UriComponentsBuilder.fromHttpUrl(flaskApiBaseUrl + "/fetch_weekly_data/" + gameweek)
                .toUriString();
        ResponseEntity<PlayerDTO[]> response = restTemplate.exchange(url, HttpMethod.GET, null, PlayerDTO[].class);
        return Arrays.asList(response.getBody());
    }

    // Fetch total player data from the optimal team route
    public List<PlayerDTO> fetchTotalPlayerData() {
        String url = UriComponentsBuilder.fromHttpUrl(flaskApiBaseUrl + "/optimal_team")
                .toUriString();
        ResponseEntity<PlayerDTO[]> response = restTemplate.exchange(url, HttpMethod.GET, null, PlayerDTO[].class);
        return Arrays.asList(response.getBody());
    }
}
