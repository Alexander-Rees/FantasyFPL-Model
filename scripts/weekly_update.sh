#!/usr/bin/env bash
# Weekly FPL Data Update Script
# Automates: Data ingestion, ML retraining, Article scraping, Vector DB update
# Run this script every week before the gameweek deadline

set -e  # Exit on error

echo "🚀 Starting Weekly FPL Update..."
echo "=================================="

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Loaded environment variables"
else
    echo "❌ .env file not found!"
    exit 1
fi

# Step 1: Ingest latest FPL player data
echo ""
echo "📊 Step 1/4: Ingesting FPL player data..."
cd flask-api
python scripts/ingest_elo_and_fpl.py
if [ $? -eq 0 ]; then
    echo "✅ FPL data ingestion complete"
else
    echo "❌ FPL data ingestion failed"
    exit 1
fi
cd ..

# Step 2: Retrain ML model with latest data
echo ""
echo "🤖 Step 2/4: Retraining ML model..."
cd flask-api
python train_model.py
if [ $? -eq 0 ]; then
    echo "✅ ML model retraining complete"
else
    echo "❌ ML model retraining failed"
    exit 1
fi
cd ..

# Step 3: Scrape latest FPL articles
echo ""
echo "📰 Step 3/4: Scraping latest FPL articles..."
cd llm-service/scraper
python weekly_scraper.py --max-articles 20
if [ $? -eq 0 ]; then
    echo "✅ Article scraping complete"
else
    echo "❌ Article scraping failed"
    exit 1
fi
cd ../..

# Step 4: Ingest articles into vector database
echo ""
echo "🔍 Step 4/4: Updating vector database..."
cd llm-service
python tests/test_ingestion.py
if [ $? -eq 0 ]; then
    echo "✅ Vector database update complete"
else
    echo "❌ Vector database update failed"
    exit 1
fi
cd ..

echo ""
echo "=================================="
echo "✅ Weekly update complete!"
echo ""
echo "📊 Summary:"
echo "  - FPL player data: Updated"
echo "  - ML predictions: Retrained"
echo "  - Expert articles: Scraped"
echo "  - RAG system: Updated"
echo ""
echo "🎯 Your FPL AI is ready for the new gameweek!"
