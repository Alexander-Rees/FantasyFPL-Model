// src/main/java/com/example/demo/controller/UserController.java
package com.example.demo.controller;

import com.example.demo.dto.LoginResponseDTO;
import com.example.demo.model.User;
import com.example.demo.service.UserService;
import com.example.demo.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;
    
    @Autowired
    private JwtUtil jwtUtil;

    @GetMapping
    public List<User> getAllUsers() {
        return userService.getAllUsers();
    }

    @PostMapping("/register")
    public User createUser(@RequestBody User user) {
        return userService.saveUser(user);
    }

    @PostMapping("/login")
    public LoginResponseDTO loginUser(@RequestBody User user) {
        User loggedInUser = userService.loginUser(user);
        String token = jwtUtil.generateToken(loggedInUser.getEmail(), loggedInUser.getId());
        
        return new LoginResponseDTO(
            loggedInUser.getId(),
            loggedInUser.getName(),
            loggedInUser.getEmail(),
            token
        );
    }
}
