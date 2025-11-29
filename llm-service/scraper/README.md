# Weekly FPL Content Scraper

Automatically scrapes FPL expert content organized by gameweek for time-relevant RAG context.

## Features

- ✅ Auto-detects current gameweek from FPL API
- ✅ Organizes articles by gameweek (`data/raw/scraped/gw12/`, `gw13/`, etc.)
- ✅ Saves metadata for each gameweek
- ✅ Supports manual gameweek specification
- ✅ Ready for weekly cron scheduling

## Directory Structure

```
data/raw/scraped/
├── gw12/
│   ├── metadata.json
│   ├── captaincy_gw12-captain-picks.md
│   ├── transfers_gw12-transfer-tips.md
│   └── fixtures_gw12-fixture-analysis.md
├── gw13/
│   ├── metadata.json
│   └── ...
└── gw14/
    └── ...
```

## Usage

### Manual Run (Current Gameweek)

```bash
python weekly_scraper.py
```

This will:
1. Fetch current gameweek from FPL API
2. Scrape up to 20 relevant articles
3. Save to `data/raw/scraped/gw{N}/`

### Specify Gameweek

```bash
python weekly_scraper.py --gameweek 13
```

### Adjust Article Limit

```bash
python weekly_scraper.py --max-articles 50
```

## Automated Weekly Scraping

### Option 1: Cron Job (Recommended)

Add to your crontab to run every Monday at 9 AM:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path):
0 9 * * 1 /Users/arees/fantasy-soccer-app/llm-service/scraper/weekly_scrape.sh
```

### Option 2: Manual Weekly Run

```bash
./weekly_scrape.sh
```

Logs are saved to `logs/scraper_YYYYMMDD_HHMMSS.log`

## Metadata Format

Each gameweek directory includes a `metadata.json`:

```json
{
  "gameweek": 12,
  "scraped_at": "2025-11-21T12:15:00",
  "articles": [
    {
      "filename": "captaincy_gw12-captain-picks.md",
      "title": "GW12 Captain Picks",
      "category": "captaincy",
      "url": "https://..."
    }
  ]
}
```

## RAG Integration

The LLM service can use gameweek-specific context:

```python
# Load articles for current gameweek
current_gw = 12
articles_dir = Path(f"data/raw/scraped/gw{current_gw}")

# This ensures RAG uses fresh, relevant content
```

## Categories

Articles are automatically categorized:
- `captaincy` - Captain picks and analysis
- `transfers` - Transfer suggestions
- `fixtures` - Fixture difficulty analysis
- `differentials` - Differential picks
- `general` - General FPL strategy

## Troubleshooting

**Can't detect gameweek:**
- Check FPL API is accessible: `curl https://fantasy.premierleague.com/api/bootstrap-static/`
- Manually specify: `python weekly_scraper.py --gameweek 12`

**No articles found:**
- FPL Scout may not have published GW content yet
- Try again closer to gameweek deadline
- Check website is accessible

## Next Steps

1. Run initial scrape for current gameweek
2. Set up weekly cron job
3. Integrate with RAG system to use gameweek-specific context
