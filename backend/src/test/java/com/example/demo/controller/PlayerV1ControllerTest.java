package com.example.demo.controller;

import com.example.demo.dto.PlayerDTO;
import com.example.demo.service.PlayerDataService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

class PlayerV1ControllerTest {

    @Mock
    private PlayerDataService playerDataService;

    @InjectMocks
    private PlayerController playerController;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testGetPlayerData() {
        // Arrange
        PlayerDTO player1 = new PlayerDTO();
        player1.setId(1L);
        player1.setName("Test Player 1");
        player1.setTeam("Arsenal");
        player1.setPosition("MID");
        
        PlayerDTO player2 = new PlayerDTO();
        player2.setId(2L);
        player2.setName("Test Player 2");
        player2.setTeam("Chelsea");
        player2.setPosition("DEF");
        
        List<PlayerDTO> players = Arrays.asList(player1, player2);
        when(playerDataService.getAllPlayers()).thenReturn(players);

        // Act
        List<PlayerDTO> result = playerController.getPlayerData(0, 10, null, null, null);

        // Assert
        assertNotNull(result);
        assertEquals(2, result.size());
        assertEquals("Test Player 1", result.get(0).getName());
    }

    @Test
    void testGetPlayerDataWithTeamFilter() {
        // Arrange
        PlayerDTO player1 = new PlayerDTO();
        player1.setId(1L);
        player1.setName("Test Player 1");
        player1.setTeam("Arsenal");
        
        PlayerDTO player2 = new PlayerDTO();
        player2.setId(2L);
        player2.setName("Test Player 2");
        player2.setTeam("Chelsea");
        
        List<PlayerDTO> players = Arrays.asList(player1, player2);
        when(playerDataService.getAllPlayers()).thenReturn(players);

        // Act
        List<PlayerDTO> result = playerController.getPlayerData(0, 10, "Arsenal", null, null);

        // Assert
        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("Arsenal", result.get(0).getTeam());
    }

    @Test
    void testGetPlayerDataWithPagination() {
        // Arrange
        PlayerDTO player1 = new PlayerDTO();
        player1.setId(1L);
        player1.setName("Player 1");
        
        PlayerDTO player2 = new PlayerDTO();
        player2.setId(2L);
        player2.setName("Player 2");
        
        PlayerDTO player3 = new PlayerDTO();
        player3.setId(3L);
        player3.setName("Player 3");
        
        List<PlayerDTO> players = Arrays.asList(player1, player2, player3);
        when(playerDataService.getAllPlayers()).thenReturn(players);

        // Act - request page 0, size 2
        List<PlayerDTO> result = playerController.getPlayerData(0, 2, null, null, null);

        // Assert
        assertNotNull(result);
        assertEquals(2, result.size());
        assertEquals("Player 1", result.get(0).getName());
        assertEquals("Player 2", result.get(1).getName());
    }
}

