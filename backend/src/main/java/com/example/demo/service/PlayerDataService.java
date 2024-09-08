package com.example.demo.service;

import com.example.demo.dto.PlayerDTO;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;

@Service
public class PlayerDataService {

    // Mock data for weekly player data for a specific gameweek
    public List<PlayerDTO> fetchWeeklyPlayerData(int gameweek) {
        // Mock response with fields matching PlayerDTO structure
        return Arrays.asList(
                createPlayer(1L, "Player 1", "Team A", false, 4, 7.5, 100, 10),
                createPlayer(2L, "Player 2", "Team B", true, 3, 8.0, 95, 8),
                createPlayer(3L, "Player 3", "Team C", false, 2, 6.5, 90, 6));
    }

    // Mock data for total player data from the optimal team route
    public List<PlayerDTO> fetchTotalPlayerData() {
        // Mock response with fields matching PlayerDTO structure
        return Arrays.asList(
                createPlayer(4L, "Player 4", "Team D", false, 1, 5.0, 120, 12),
                createPlayer(5L, "Player 5", "Team E", false, 2, 6.5, 110, 9),
                createPlayer(6L, "Player 6", "Team F", false, 3, 9.0, 115, 11),
                createPlayer(7L, "Player 7", "Team G", false, 4, 10.5, 130, 15));
    }

    // Helper method to create PlayerDTO objects
    private PlayerDTO createPlayer(Long id, String name, String team, boolean injured, int position, double value,
            int totalPoints, int weeklyPoints) {
        PlayerDTO player = new PlayerDTO();
        player.setId(id);
        player.setName(name);
        player.setTeam(team);
        player.setInjured(injured);
        player.setPosition(position);
        player.setValue(value);
        player.setTotalPoints(totalPoints);
        player.setWeeklyPoints(weeklyPoints);
        return player;
    }
}
