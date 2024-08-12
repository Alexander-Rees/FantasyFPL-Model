package com.example.demo.service;

import com.example.demo.model.Player;
import com.example.demo.model.Team;
import com.example.demo.model.User;
import com.example.demo.repository.TeamRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class TeamService {
    @Autowired
    private TeamRepository teamRepository;

    public Team getTeamByUserId(Long userId) {
        return teamRepository.findByUserId(userId);
    }

    public Team addPlayerToTeam(Long userId, Player player) {
        Team team = teamRepository.findByUserId(userId);
        if (team == null) {
            team = new Team();
            team.setUser(new User(userId)); // Create a new User object with the given userId
        }
        team.getPlayers().add(player);
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
}
