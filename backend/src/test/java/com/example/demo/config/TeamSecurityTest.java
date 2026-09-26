package com.example.demo.config;

import com.example.demo.controller.TeamController;
import com.example.demo.model.Team;
import com.example.demo.service.FplImportService;
import com.example.demo.service.TeamOptimizationService;
import com.example.demo.service.TeamService;
import com.example.demo.util.JwtUtil;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Import;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = TeamController.class)
@Import({SecurityConfig.class, JwtUtil.class})
@TestPropertySource(properties = "jwt.secret=test-jwt-secret-not-for-production-use")
class TeamSecurityTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtUtil jwtUtil;

    @MockBean
    private TeamService teamService;

    @MockBean
    private FplImportService fplImportService;

    @MockBean
    private TeamOptimizationService teamOptimizationService;

    @MockBean
    private StringRedisTemplate redisTemplate;

    @MockBean
    private RestTemplateBuilder restTemplateBuilder;

    @Test
    void teamRequiresJwt() throws Exception {
        mockMvc.perform(get("/api/v1/team").param("userId", "1"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void optimizeRequiresJwt() throws Exception {
        mockMvc.perform(post("/api/v1/team/optimize")
                        .param("userId", "1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"budget\":100.0,\"freeTransfers\":1,\"formation\":\"3-4-3\"}"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void teamAllowsValidJwt() throws Exception {
        when(teamService.getTeamByUserId(anyLong())).thenReturn(new Team());
        String token = jwtUtil.generateToken("manager@example.com", 1L);

        mockMvc.perform(get("/api/v1/team")
                        .param("userId", "1")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk());
    }
}
