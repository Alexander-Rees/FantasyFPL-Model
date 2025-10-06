#!/usr/bin/env python3
"""
Test script for FPL data ingestion
"""

import os
import sys
import logging

# Add the parent directory to the path so we can import the main script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.ingest_elo_and_fpl import main

if __name__ == "__main__":
    # Set up environment variables for testing
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_USER'] = 'root'
    os.environ['DB_PASSWORD'] = 'password'  # Update with your actual password
    os.environ['DB_NAME'] = 'fpl_optimization'
    
    # Run the ingestion
    main()
