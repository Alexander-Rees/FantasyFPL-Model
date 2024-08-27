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

    public Team addPlayerToTeam(Long userId, Player player) {
        Team team = teamRepository.findByUserId(userId);
        if (team == null) {
            team = new Team();
            team.setUser(new User(userId)); // Assuming the user already exists with this ID
        }

        // Ensure the Player ID is not null
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

    public Team removePlayerFromTeam(Long userId, Long playerId) {
        Team team = teamRepository.findByUserId(userId);
        if (team != null) {
            team.getPlayers().removeIf(player -> player.getId().equals(playerId));
            return teamRepository.save(team);
        }
        return null;
    }

    public Team createTeam(CreateTeamDTO createTeamDTO) {
        // Retrieve the user by userId
        User user = userRepository.findById(createTeamDTO.getUserId()).orElseThrow();

        // Create a new team
        Team team = new Team();
        team.setName(createTeamDTO.getName());
        team.setBudget(createTeamDTO.getBudget());
        team.setUser(user);

        // Find players by their IDs and add to the team
        List<Player> players = createTeamDTO.getPlayerIds().stream()
                .map(playerId -> playerRepository.findById(playerId).orElseThrow())
                .collect(Collectors.toList());

        team.setPlayers(players);

        // Save the team in the database
        return teamRepository.save(team);
    }
}
