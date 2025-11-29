#!/bin/bash
# Collect more FPL articles for RAG knowledge base
# Run this script to scrape ~50-100 articles

cd "$(dirname "$0")"

echo "🕷️  Collecting FPL Articles for RAG Knowledge Base"
echo "=================================================="
echo ""

# Run the simple scraper multiple times with different starting points
echo "📰 Running scraper..."
python simple_scraper.py

echo ""
echo "✅ Scraping complete!"
echo ""
echo "📊 Articles collected:"
ls -1 data/raw/scraped/*.md | wc -l

echo ""
echo "📁 View articles:"
echo "   ls -lh data/raw/scraped/"
echo ""
echo "🔍 Preview an article:"
echo "   cat data/raw/scraped/general_gw12_fpl-gw12.md"
