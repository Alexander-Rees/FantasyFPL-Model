package com.example.demo.service;

import com.example.demo.dto.CreateTeamDTO;
import com.example.demo.model.Player;
import com.example.demo.model.Team;
import com.example.demo.model.User;
import com.example.demo.repository.PlayerRepository;
import com.example.demo.repository.TeamRepository;
import com.example.demo.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class TeamService {
    @Autowired
    private TeamRepository teamRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PlayerRepository playerRepository;

    @Autowired
    private RestTemplate restTemplate; // Inject RestTemplate

    // Method to call the Flask API and get the optimal team
    public String getOptimalTeam() {
        String flaskApiUrl = "http://127.0.0.1:5000/optimal_team"; // Flask API URL
        ResponseEntity<String> response = restTemplate.getForEntity(flaskApiUrl, String.class);
        return response.getBody(); // Returns the JSON response from the Flask API
    }

    // Method to call the Flask API and get top players by position
    public String getTopPlayers() {
        String flaskApiUrl = "http://127.0.0.1:5000/top_players"; // Flask API URL
        ResponseEntity<String> response = restTemplate.getForEntity(flaskApiUrl, String.class);
        return response.getBody();
    }

    // Existing method to get a team by user ID
    public Team getTeamByUserId(Long userId) {
        return teamRepository.findByUserId(userId);
    }

    // Existing method to add a player to a team
    public Team addPlayerToTeam(Long userId, Player player) {
        Team team = teamRepository.findByUserId(userId);
        if (team == null) {
            team = new Team();
            team.setUser(new User(userId)); // Assuming the user already exists with this ID
        }

        if (player.getId() == null) {
            throw new IllegalArgumentException("Player ID must not be null");
        }

        Player existingPlayer = playerRepository.findById(player.getId())
                .orElseThrow(() -> new IllegalArgumentException("Player not found"));

        if (!team.getPlayers().contains(existingPlayer)) {
            team.getPlayers().add(existingPlayer);
        }

        return teamRepository.save(team);
    }

    // Existing method to remove a player from a team
    public Team removePlayerFromTeam(Long userId, Long playerId) {
        Team team = teamRepository.findByUserId(userId);
        if (team != null) {
            team.getPlayers().removeIf(player -> player.getId().equals(playerId));
            return teamRepository.save(team);
        }
        return null;
    }

    // Existing method to create a new team
    public Team createTeam(CreateTeamDTO createTeamDTO) {
        User user = userRepository.findById(createTeamDTO.getUserId()).orElseThrow();

        Team team = new Team();
        team.setName(createTeamDTO.getName());
        team.setBudget(createTeamDTO.getBudget());
        team.setUser(user);

        List<Player> players = createTeamDTO.getPlayerIds().stream()
                .map(playerId -> playerRepository.findById(playerId).orElseThrow())
                .collect(Collectors.toList());

        team.setPlayers(players);

        return teamRepository.save(team);
    }
}
