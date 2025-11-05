package com.example.demo.service;

import com.example.demo.dto.PlayerDTO;
import com.example.demo.model.Player;
import com.example.demo.repository.PlayerRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

class PlayerDataServiceTest {

    @Mock
    private PlayerRepository playerRepository;

    @InjectMocks
    private PlayerDataService playerDataService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testGetAllPlayers() {
        // Arrange
        Player player1 = new Player();
        player1.setId(1L);
        player1.setName("Player 1");
        player1.setPosition("MID");
        player1.setTeam("Arsenal");
        player1.setValue(5.0);
        
        Player player2 = new Player();
        player2.setId(2L);
        player2.setName("Player 2");
        player2.setPosition("DEF");
        player2.setTeam("Chelsea");
        player2.setValue(4.5);
        
        List<Player> players = Arrays.asList(player1, player2);
        when(playerRepository.findAll()).thenReturn(players);

        // Act
        List<PlayerDTO> result = playerDataService.getAllPlayers();

        // Assert
        assertNotNull(result);
        assertEquals(2, result.size());
        assertEquals("Player 1", result.get(0).getName());
        assertEquals("MID", result.get(0).getPosition());
        assertEquals("Arsenal", result.get(0).getTeam());
    }

    @Test
    void testConvertToDTO() {
        // Arrange
        Player player = new Player();
        player.setId(1L);
        player.setName("Test Player");
        player.setPosition("FWD");
        player.setTeam("Liverpool");
        player.setValue(8.5);
        player.setTotalPoints(100);
        player.setWeeklyPoints(10);

        // Act
        PlayerDTO dto = playerDataService.convertToDTO(player);

        // Assert
        assertNotNull(dto);
        assertEquals(1L, dto.getId());
        assertEquals("Test Player", dto.getName());
        assertEquals("FWD", dto.getPosition());
        assertEquals("Liverpool", dto.getTeam());
        assertEquals(8.5, dto.getValue());
        assertEquals(100, dto.getTotalPoints());
        assertEquals(10, dto.getWeeklyPoints());
    }
}

