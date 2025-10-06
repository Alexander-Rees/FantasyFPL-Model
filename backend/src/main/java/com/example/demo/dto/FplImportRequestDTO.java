package com.example.demo.dto;

public class FplImportRequestDTO {
    private Long entryId; // FPL entry ID
    
    public FplImportRequestDTO() {}
    
    public FplImportRequestDTO(Long entryId) {
        this.entryId = entryId;
    }
    
    // Getters and setters
    public Long getEntryId() {
        return entryId;
    }
    
    public void setEntryId(Long entryId) {
        this.entryId = entryId;
    }
}
