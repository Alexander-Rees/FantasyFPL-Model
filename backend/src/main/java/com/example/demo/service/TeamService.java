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


    public Team getTeamByUserId(Long userId) {
        return teamRepository.findByUserId(userId);
    }

    // Updated method to accept playerId instead of full Player object
    public Team addPlayerToTeam(Long userId, Long playerId) {
        Team team = getTeamByUserId(userId);
        Player player = playerRepository.findById(playerId).orElseThrow(() -> new RuntimeException("Player not found"));

        // Check if player is already on the team
        if (team.getPlayers().contains(player)) {
            throw new RuntimeException("Player is already in the team");
        }

        // Check if team has enough budget
        if (team.getBudget() < player.getValue()) {
            throw new RuntimeException("Not enough budget to add this player");
        }

        // Add the player to the team
        team.getPlayers().add(player);
        team.setBudget(team.getBudget() - player.getValue());

        // Save the updated team
        return teamRepository.save(team);
    }

    public Team removePlayerFromTeam(Long userId, Long playerId) {
        Team team = teamRepository.findByUserId(userId);

        if (team == null) {
            throw new IllegalArgumentException("Team not found for the user");
        }

        // Find the player to be removed
        Player playerToRemove = playerRepository.findById(playerId)
                .orElseThrow(() -> new IllegalArgumentException("Player not found"));

        // Remove player from team if present
        boolean removed = team.getPlayers().removeIf(player -> player.getId().equals(playerId));

        if (removed) {
            // Refund the budget
            team.setBudget(team.getBudget() + playerToRemove.getValue());
            return teamRepository.save(team);
        } else {
            throw new IllegalArgumentException("Player not found in the team");
        }
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
        // TODO: Implement team optimization logic using database data
        // This should use the player data from the database and apply optimization algorithms
        return "Team optimization feature coming soon - will use database player data";
    }

    public String getTopPlayers() {
        // TODO: Implement top players logic using database data
        // This should query the database for top performing players
        return "Top players feature coming soon - will use database player data";
    }
}
