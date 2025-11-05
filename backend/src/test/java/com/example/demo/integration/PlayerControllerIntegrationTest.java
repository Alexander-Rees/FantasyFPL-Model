package com.example.demo.integration;

import com.example.demo.model.Player;
import com.example.demo.repository.PlayerRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureWebMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.WebApplicationContext;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.MOCK)
@AutoConfigureWebMvc
@ActiveProfiles("test")
@Transactional
class PlayerControllerIntegrationTest {

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private PlayerRepository playerRepository;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
        
        // Create test data - ensure schema is created first
        Player testPlayer = new Player();
        testPlayer.setName("Test Player");
        testPlayer.setPosition("MID");
        testPlayer.setTeam("Arsenal");
        testPlayer.setValue(50.0);
        testPlayer.setTotalPoints(100);
        testPlayer.setWeeklyPoints(10);
        testPlayer.setFplId(1L);
        playerRepository.saveAndFlush(testPlayer);
    }

    @Test
    void testGetPlayersEndpoint() throws Exception {
        mockMvc.perform(get("/api/v1/players"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("application/json"));
    }

    @Test
    void testGetPlayersWithPagination() throws Exception {
        mockMvc.perform(get("/api/v1/players")
                .param("page", "0")
                .param("size", "5"))
                .andExpect(status().isOk());
    }

    @Test
    void testGetPlayersWithTeamFilter() throws Exception {
        mockMvc.perform(get("/api/v1/players")
                .param("team", "Arsenal"))
                .andExpect(status().isOk());
    }
}

