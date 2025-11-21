#!/bin/bash
# Weekly retraining workflow
# Run this script every Monday after the gameweek ends

set -e  # Exit on error

echo "🔄 Starting weekly model retraining..."
echo "=================================="

# Navigate to flask-api directory
cd "$(dirname "$0")/../flask-api"

# Step 1: Fetch latest gameweek data
echo ""
echo "📥 Step 1: Fetching latest gameweek data..."
python fetch_gameweek_data.py

# Step 2: Retrain model with updated data
echo ""
echo "🤖 Step 2: Retraining model with recency weighting..."
python train_model.py

# Step 3: Generate new predictions
echo ""
echo "🎯 Step 3: Generating predictions for active players..."
python predict_current.py

echo ""
echo "✅ Weekly retraining complete!"
echo "=================================="
echo "Model has been updated with latest gameweek data"
echo "Predictions have been refreshed in the database"
