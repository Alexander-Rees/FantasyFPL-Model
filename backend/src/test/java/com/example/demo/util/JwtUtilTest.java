package com.example.demo.util;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class JwtUtilTest {

    private static final String SECRET = "test-jwt-secret-not-for-production-use";

    @Test
    void generateAndValidateToken() {
        JwtUtil jwtUtil = new JwtUtil(SECRET);
        String token = jwtUtil.generateToken("manager@example.com", 42L);

        assertEquals("manager@example.com", jwtUtil.extractEmail(token));
        assertEquals(42L, jwtUtil.extractUserId(token));
        assertTrue(jwtUtil.validateToken(token, "manager@example.com"));
        assertFalse(jwtUtil.isTokenExpired(token));
    }

    @Test
    void rejectsShortSecret() {
        IllegalStateException error = assertThrows(IllegalStateException.class, () -> new JwtUtil("too-short"));
        assertTrue(error.getMessage().contains("32"));
    }

    @Test
    void rejectsTamperedToken() {
        JwtUtil issuer = new JwtUtil(SECRET);
        JwtUtil otherKey = new JwtUtil("another-jwt-secret-not-for-production");
        String token = issuer.generateToken("manager@example.com", 1L);
        assertThrows(Exception.class, () -> otherKey.extractEmail(token));
    }
}
