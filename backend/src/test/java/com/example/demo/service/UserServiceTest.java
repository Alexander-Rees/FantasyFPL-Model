package com.example.demo.service;

import com.example.demo.model.User;
import com.example.demo.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    private User requestUser;

    @BeforeEach
    void setUp() {
        requestUser = new User();
        requestUser.setEmail("manager@example.com");
        requestUser.setName("Manager");
        requestUser.setPassword("plain-password");
    }

    @Test
    void saveUserHashesPasswordBeforePersist() {
        when(passwordEncoder.encode("plain-password")).thenReturn("hashed-password");
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> invocation.getArgument(0));

        User saved = userService.saveUser(requestUser);

        ArgumentCaptor<User> captor = ArgumentCaptor.forClass(User.class);
        verify(userRepository).save(captor.capture());
        assertEquals("hashed-password", captor.getValue().getPassword());
        assertEquals("hashed-password", saved.getPassword());
        verify(passwordEncoder).encode("plain-password");
    }

    @Test
    void loginUserSucceedsAndClearsPassword() {
        User stored = new User();
        stored.setId(7L);
        stored.setEmail("manager@example.com");
        stored.setName("Manager");
        stored.setPassword("hashed-password");

        when(userRepository.findByEmail("manager@example.com")).thenReturn(stored);
        when(passwordEncoder.matches("plain-password", "hashed-password")).thenReturn(true);

        User loggedIn = userService.loginUser(requestUser);

        assertEquals(7L, loggedIn.getId());
        assertNull(loggedIn.getPassword());
    }

    @Test
    void loginUserThrowsWhenEmailUnknown() {
        when(userRepository.findByEmail(anyString())).thenReturn(null);

        RuntimeException ex = assertThrows(RuntimeException.class, () -> userService.loginUser(requestUser));
        assertTrue(ex.getMessage().contains("User not found"));
    }

    @Test
    void loginUserThrowsWhenPasswordInvalid() {
        User stored = new User();
        stored.setEmail("manager@example.com");
        stored.setPassword("hashed-password");
        when(userRepository.findByEmail("manager@example.com")).thenReturn(stored);
        when(passwordEncoder.matches("plain-password", "hashed-password")).thenReturn(false);

        RuntimeException ex = assertThrows(RuntimeException.class, () -> userService.loginUser(requestUser));
        assertTrue(ex.getMessage().contains("Invalid password"));
    }
}
