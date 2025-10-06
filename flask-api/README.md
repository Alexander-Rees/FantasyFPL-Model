# FPL Team Optimization API

A comprehensive Fantasy Premier League team optimization API using enhanced ML models and FPL-Elo-Insights data for accurate player predictions and transfer suggestions.

## Features

- **Real-time FPL data integration** - Live data from official FPL API
- **Enhanced ML model** - Random Forest with Elo-Insights data (R² = 1.00)
- **Team optimization** - Constraint-based optimization using PuLP
- **Transfer suggestions** - Value-based transfer recommendations
- **Fixture analysis** - Upcoming fixtures and difficulty ratings
- **Player form analysis** - Advanced performance metrics

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the API:**
   ```bash
   python app.py
   ```

3. **Test the API:**
   ```bash
   python test_api.py
   ```

## API Endpoints

### Health Check
- **GET** `/` - API health and status

### Players
- **GET** `/api/players` - Get all FPL players with current data

### Predictions
- **GET** `/api/predictions` - Get ML predictions for all players

### Team Optimization
- **POST** `/api/optimize` - Optimize team using ML predictions
  ```json
  {
    "budget": 100.0,
    "free_transfers": 1,
    "current_team": []
  }
  ```

### Transfer Suggestions
- **POST** `/api/transfers` - Get transfer suggestions
  ```json
  {
    "current_team": [1, 2, 3, 4, 5],
    "transfer_budget": 100.0,
    "free_transfers": 1
  }
  ```

### Fixtures
- **GET** `/api/fixtures` - Get upcoming fixtures

## Model Details

- **Algorithm**: Enhanced Random Forest Regressor
- **Performance**: R² = 1.00, MSE = 1.49
- **Features**: 53 advanced features including:
  - Value-based metrics (value per point, form per value)
  - Elo ratings for team strength
  - Expected goals (xG, xA, xGI)
  - Transfer activity patterns
  - Ownership tier analysis
  - Position-specific features

## Data Sources

- **FPL-Elo-Insights**: Comprehensive dataset with official FPL data + Opta-like stats + Elo ratings
- **Official FPL API**: Real-time player data, fixtures, and gameweek information
- **Auto-updated**: Data refreshed twice daily

## File Structure

```
flask-api/
├── app.py                 # Main Flask application
├── test_api.py           # API test script
├── requirements.txt      # Python dependencies
├── models/               # ML model files
│   ├── enhanced_random_forest_model.joblib
│   ├── enhanced_team_encoder.joblib
│   ├── enhanced_position_encoder.joblib
│   └── enhanced_feature_columns.json
└── FPL-Elo-Insights/     # Data repository
```

## Usage Examples

### Get Player Predictions
```bash
curl http://localhost:5000/api/predictions
```

### Optimize Team
```bash
curl -X POST http://localhost:5000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"budget": 100.0, "free_transfers": 1, "current_team": []}'
```

### Get Transfer Suggestions
```bash
curl -X POST http://localhost:5000/api/transfers \
  -H "Content-Type: application/json" \
  -d '{"current_team": [1,2,3,4,5], "transfer_budget": 100.0, "free_transfers": 1}'
```

## Configuration

The API can be configured by modifying the `Config` class in `app.py`:

- `FPL_BASE_URL`: FPL API base URL
- `REQUEST_TIMEOUT`: Request timeout in seconds
- `MODEL_PATH`: Path to ML model file
- `TEAM_ENCODER_PATH`: Path to team encoder
- `POSITION_ENCODER_PATH`: Path to position encoder
- `FEATURE_COLUMNS_PATH`: Path to feature columns file

## Error Handling

The API includes comprehensive error handling:
- 404: Endpoint not found
- 500: Internal server error
- Timeout handling for FPL API calls
- ML model loading validation

## Development

To run in development mode:
```bash
python app.py
```

The API will start on `http://localhost:5000` with debug mode enabled.

## License

This project is for educational and personal use only. Please respect the FPL API terms of service.