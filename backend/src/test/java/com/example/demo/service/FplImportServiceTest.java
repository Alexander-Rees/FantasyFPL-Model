package com.example.demo.service;

import com.example.demo.model.Player;
import com.example.demo.model.Team;
import com.example.demo.model.User;
import com.example.demo.repository.PlayerRepository;
import com.example.demo.repository.TeamRepository;
import com.example.demo.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class FplImportServiceTest {

    @Mock
    private PlayerRepository playerRepository;
    @Mock
    private TeamRepository teamRepository;
    @Mock
    private UserRepository userRepository;
    @Mock
    private RestTemplate restTemplate;

    private FplImportService fplImportService;

    @BeforeEach
    void setUp() {
        fplImportService = new FplImportService(restTemplate);
        // Inject mocks into @Autowired fields
        org.springframework.test.util.ReflectionTestUtils.setField(fplImportService, "playerRepository",
                playerRepository);
        org.springframework.test.util.ReflectionTestUtils.setField(fplImportService, "teamRepository", teamRepository);
        org.springframework.test.util.ReflectionTestUtils.setField(fplImportService, "userRepository", userRepository);
    }

    @Test
    void importTeamFromFplMapsPicksToPlayersAndSetsBudget() {
        User user = new User();
        user.setId(1L);
        user.setEmail("manager@example.com");
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(teamRepository.findByUserId(1L)).thenReturn(null);
        when(teamRepository.save(any(Team.class))).thenAnswer(invocation -> {
            Team team = invocation.getArgument(0);
            if (team.getId() == null) {
                team.setId(99L);
            }
            return team;
        });
        when(playerRepository.count()).thenReturn(2L);

        Player p1 = player(10L, 101L, "Salah", 12.5);
        Player p2 = player(11L, 102L, "Haaland", 14.0);
        when(playerRepository.findByFplId(101L)).thenReturn(Optional.of(p1));
        when(playerRepository.findByFplId(102L)).thenReturn(Optional.of(p2));

        Map<String, Object> bootstrap = new HashMap<>();
        Map<String, Object> currentEvent = new HashMap<>();
        currentEvent.put("id", 1);
        bootstrap.put("current-event", currentEvent);
        when(restTemplate.getForEntity(contains("/bootstrap-static/"), eq(Map.class)))
                .thenReturn(new ResponseEntity<>(bootstrap, HttpStatus.OK));

        Map<String, Object> picksBody = new HashMap<>();
        List<Map<String, Object>> picks = new ArrayList<>();
        picks.add(Map.of("element", 101));
        picks.add(Map.of("element", 102));
        picksBody.put("picks", picks);
        when(restTemplate.getForEntity(contains("/entry/42/event/1/picks/"), eq(Map.class)))
                .thenReturn(new ResponseEntity<>(picksBody, HttpStatus.OK));

        Team result = fplImportService.importTeamFromFpl(1L, 42L);

        assertEquals(2, result.getPlayers().size());
        assertEquals(100.0 - 12.5 - 14.0, result.getBudget(), 0.001);
        assertTrue(result.getName().contains("FPL Team 42"));
    }

    @Test
    void importTeamFromFplFailsWhenUserMissing() {
        when(userRepository.findById(99L)).thenReturn(Optional.empty());
        when(userRepository.findAll()).thenReturn(Collections.emptyList());

        Map<String, Object> bootstrap = new HashMap<>();
        Map<String, Object> currentEvent = new HashMap<>();
        currentEvent.put("id", 1);
        bootstrap.put("current-event", currentEvent);
        when(restTemplate.getForEntity(contains("/bootstrap-static/"), eq(Map.class)))
                .thenReturn(new ResponseEntity<>(bootstrap, HttpStatus.OK));

        Map<String, Object> picksBody = Map.of("picks", List.of(Map.of("element", 1)));
        when(restTemplate.getForEntity(contains("/picks/"), eq(Map.class)))
                .thenReturn(new ResponseEntity<>(picksBody, HttpStatus.OK));

        RuntimeException ex = assertThrows(RuntimeException.class,
                () -> fplImportService.importTeamFromFpl(99L, 1L));
        assertTrue(ex.getMessage().contains("User not found"));
    }

    @Test
    void getTeamPlayersReturnsEmptyWhenNoTeam() {
        when(teamRepository.findByUserId(5L)).thenReturn(null);
        assertTrue(fplImportService.getTeamPlayers(5L).isEmpty());
    }

    private static Player player(Long id, Long fplId, String name, double value) {
        Player player = new Player();
        player.setId(id);
        player.setFplId(fplId);
        player.setName(name);
        player.setValue(value);
        player.setPosition("MID");
        player.setTeam("LIV");
        return player;
    }
}
