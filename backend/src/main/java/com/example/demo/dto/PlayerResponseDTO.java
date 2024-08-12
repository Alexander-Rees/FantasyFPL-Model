package com.example.demo.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class PlayerResponseDTO {
    private List<ResponseDTO> response;

    public List<ResponseDTO> getResponse() {
        return response;
    }

    public void setResponse(List<ResponseDTO> response) {
        this.response = response;
    }
}
