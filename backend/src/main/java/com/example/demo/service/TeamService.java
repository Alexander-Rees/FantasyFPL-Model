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
    private RestTemplate restTemplate;

    public Team getTeamByUserId(Long userId) {
        return teamRepository.findByUserId(userId);
    }

    // Updated method to accept playerId instead of full Player object
    public Team addPlayerToTeam(Long userId, Long playerId) {
        Team team = teamRepository.findByUserId(userId);

        if (team == null) {
            throw new IllegalArgumentException("Team not found for the user");
        }

        // Fetch player by playerId
        Player player = playerRepository.findById(playerId)
                .orElseThrow(() -> new IllegalArgumentException("Player not found"));

        // Add player to team if not already present
        if (!team.getPlayers().contains(player)) {
            team.getPlayers().add(player);
        } else {
            throw new IllegalArgumentException("Player already in the team");
        }

        // Save and return the updated team
        return teamRepository.save(team);
    }

    public Team removePlayerFromTeam(Long userId, Long playerId) {
        Team team = teamRepository.findByUserId(userId);

        if (team != null) {
            team.getPlayers().removeIf(player -> player.getId().equals(playerId));
            return teamRepository.save(team);
        }

        return null;
    }

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

    public String getOptimalTeam() {
        String flaskApiUrl = "http://127.0.0.1:5000/optimal_team";
        ResponseEntity<String> response = restTemplate.getForEntity(flaskApiUrl, String.class);
        return response.getBody();
    }

    public String getTopPlayers() {
        String flaskApiUrl = "http://127.0.0.1:5000/top_players";
        ResponseEntity<String> response = restTemplate.getForEntity(flaskApiUrl, String.class);
        return response.getBody();
    }
}
