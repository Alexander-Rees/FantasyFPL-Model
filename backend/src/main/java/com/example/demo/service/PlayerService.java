package com.example.demo.service;

import com.example.demo.model.Player;
import com.example.demo.repository.PlayerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PlayerService {
    @Autowired
    private PlayerRepository playerRepository;

    public List<Player> getAllPlayers() {
        return playerRepository.findAll();
    }
}
