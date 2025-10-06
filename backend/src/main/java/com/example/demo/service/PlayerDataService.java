package com.example.demo.service;

import com.example.demo.dto.PlayerDTO;
import com.example.demo.model.Player;
import com.example.demo.repository.PlayerRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class PlayerDataService {

    private final PlayerRepository playerRepository;

    public PlayerDataService(PlayerRepository playerRepository) {
        this.playerRepository = playerRepository;
    }

    // Get all players from database
    public List<PlayerDTO> getAllPlayers() {
        List<Player> players = playerRepository.findAll();
        return players.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    // Convert Player entity to PlayerDTO
    public PlayerDTO convertToDTO(Player player) {
        PlayerDTO dto = new PlayerDTO();
        dto.setId(player.getId());
        dto.setName(player.getName());
        dto.setPosition(player.getPosition());
        dto.setTeam(player.getTeam());
        dto.setValue(player.getValue());
        dto.setTotalPoints(player.getTotalPoints());
        dto.setWeeklyPoints(player.getWeeklyPoints());
        dto.setFplId(player.getFplId());
        return dto;
    }
}
