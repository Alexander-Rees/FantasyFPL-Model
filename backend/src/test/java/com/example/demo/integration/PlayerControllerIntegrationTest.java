package com.example.demo.integration;

import com.example.demo.dto.PlayerDTO;
import com.example.demo.service.PlayerDataService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Arrays;
import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for PlayerController HTTP endpoints.
 * Uses @WebMvcTest to test controller layer in isolation without database.
 */
@WebMvcTest(controllers = com.example.demo.controller.PlayerController.class,
        excludeAutoConfiguration = {
                org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class
        })
class PlayerControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PlayerDataService playerDataService;
    
    @MockBean
    private org.springframework.web.client.RestTemplate restTemplate;

    private List<PlayerDTO> testPlayers;

    @BeforeEach
    void setUp() {
        // Create test data - no database needed, service is mocked
        PlayerDTO player1 = new PlayerDTO();
        player1.setId(1L);
        player1.setName("Test Player");
        player1.setPosition("MID");
        player1.setTeam("Arsenal");
        player1.setValue(50.0);
        player1.setTotalPoints(100);
        player1.setWeeklyPoints(10);
        player1.setFplId(1L);
        
        PlayerDTO player2 = new PlayerDTO();
        player2.setId(2L);
        player2.setName("Another Player");
        player2.setPosition("DEF");
        player2.setTeam("Chelsea");
        player2.setValue(45.0);
        player2.setTotalPoints(80);
        player2.setWeeklyPoints(5);
        player2.setFplId(2L);
        
        testPlayers = Arrays.asList(player1, player2);
        when(playerDataService.getAllPlayers()).thenReturn(testPlayers);
    }

    @Test
    void testGetPlayersEndpoint() throws Exception {
        mockMvc.perform(get("/api/v1/players"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/json"));
    }

    @Test
    void testGetPlayersWithPagination() throws Exception {
        // Mock service to return paginated results
        when(playerDataService.getAllPlayers()).thenReturn(testPlayers.subList(0, 1));
        
        mockMvc.perform(get("/api/v1/players")
                .param("page", "0")
                .param("size", "1"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/json"));
    }

    @Test
    void testGetPlayersWithTeamFilter() throws Exception {
        // Mock service to return filtered results
        when(playerDataService.getAllPlayers()).thenReturn(
            testPlayers.stream()
                .filter(p -> "Arsenal".equals(p.getTeam()))
                .toList()
        );
        
        mockMvc.perform(get("/api/v1/players")
                .param("team", "Arsenal"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/json"));
    }
}

