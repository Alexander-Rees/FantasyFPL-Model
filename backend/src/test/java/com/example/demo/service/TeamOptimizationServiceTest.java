package com.example.demo.service;

import com.example.demo.dto.OptimizeRequestDTO;
import com.example.demo.dto.OptimizeResponseDTO;
import com.example.demo.dto.PlayerDTO;
import com.example.demo.model.Player;
import com.example.demo.model.Team;
import com.example.demo.model.User;
import com.example.demo.repository.PlayerRepository;
import com.example.demo.repository.TeamRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TeamOptimizationServiceTest {

    @Mock
    private TeamRepository teamRepository;
    @Mock
    private PlayerRepository playerRepository;
    @Mock
    private PlayerDataService playerDataService;
    @Mock
    private RestTemplate restTemplate;

    private TeamOptimizationService service;

    @BeforeEach
    void setUp() {
        service = new TeamOptimizationService(restTemplate);
        ReflectionTestUtils.setField(service, "teamRepository", teamRepository);
        ReflectionTestUtils.setField(service, "playerRepository", playerRepository);
        ReflectionTestUtils.setField(service, "playerDataService", playerDataService);
        ReflectionTestUtils.setField(service, "flaskApiUrl", "http://localhost:5001");
    }

    @Test
    void optimizeTeamFallsBackWhenFlaskUnavailable() {
        Team team = new Team();
        User user = new User();
        user.setId(1L);
        team.setUser(user);
        team.setPlayers(new ArrayList<>());
        when(teamRepository.findByUserId(1L)).thenReturn(team);

        List<Player> pool = List.of(
                player(1L, "GK A", "GK", 4.5, 40),
                player(2L, "DEF A", "DEF", 4.5, 50),
                player(3L, "DEF B", "DEF", 4.5, 45),
                player(4L, "DEF C", "DEF", 4.5, 44),
                player(5L, "MID A", "MID", 6.0, 70),
                player(6L, "MID B", "MID", 6.0, 65),
                player(7L, "MID C", "MID", 6.0, 60),
                player(8L, "MID D", "MID", 6.0, 55),
                player(9L, "FWD A", "FWD", 7.0, 80),
                player(10L, "FWD B", "FWD", 7.0, 75),
                player(11L, "FWD C", "FWD", 7.0, 70));
        when(playerRepository.findAll()).thenReturn(pool);
        when(playerDataService.convertToDTO(any(Player.class))).thenAnswer(invocation -> {
            Player p = invocation.getArgument(0);
            PlayerDTO dto = new PlayerDTO();
            dto.setId(p.getId());
            dto.setName(p.getName());
            dto.setPosition(p.getPosition());
            dto.setTeam(p.getTeam());
            dto.setValue(p.getValue());
            dto.setTotalPoints(p.getTotalPoints());
            return dto;
        });
        when(restTemplate.postForEntity(anyString(), any(), eq(java.util.Map.class)))
                .thenThrow(new RestClientException("flask down"));

        OptimizeRequestDTO request = new OptimizeRequestDTO();
        request.setUserId(1L);
        request.setBudget(100.0);
        request.setFormation("3-4-3");
        request.setFreeTransfers(1);

        OptimizeResponseDTO response = service.optimizeTeam(1L, request);

        assertNotNull(response);
        assertEquals("3-4-3", response.getFormation());
        assertFalse(response.getOptimalTeam().isEmpty());
        assertTrue(response.getOptimalTeam().size() <= 11);
    }

    private static Player player(Long id, String name, String position, double value, int points) {
        Player player = new Player();
        player.setId(id);
        player.setName(name);
        player.setPosition(position);
        player.setTeam("ARS");
        player.setValue(value);
        player.setTotalPoints(points);
        return player;
    }
}
