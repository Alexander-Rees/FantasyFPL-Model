#!/bin/bash
# Weekly FPL Content Scraper - Cron Job Script
# Add to crontab to run weekly: 0 9 * * 1 /path/to/weekly_scrape.sh

# Navigate to scraper directory
cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Log file
LOG_FILE="logs/scraper_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

echo "🕷️  Weekly FPL Scraper - $(date)" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"

# Run the weekly scraper
python weekly_scraper.py --max-articles 30 2>&1 | tee -a "$LOG_FILE"

# Check exit status
if [ $? -eq 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "✅ Weekly scrape completed successfully" | tee -a "$LOG_FILE"
    
    # Count total articles
    TOTAL=$(find data/raw/scraped -name "*.md" -type f | wc -l)
    echo "📊 Total articles in database: $TOTAL" | tee -a "$LOG_FILE"
else
    echo "" | tee -a "$LOG_FILE"
    echo "❌ Weekly scrape failed" | tee -a "$LOG_FILE"
fi

echo "================================================" | tee -a "$LOG_FILE"
