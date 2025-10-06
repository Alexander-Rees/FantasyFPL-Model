# GitHub Actions Workflows

## FPL Data Ingestion

This workflow automatically ingests fresh FPL data twice daily at 05:15 and 17:15 UTC.

### Setup

1. **Repository Secrets**: Add the following secrets to your GitHub repository:
   - `DB_HOST`: MySQL host (default: localhost)
   - `DB_USER`: MySQL username (default: root)  
   - `DB_PASSWORD`: MySQL password (required)
   - `DB_NAME`: MySQL database name (default: fpl_optimization)

2. **Manual Trigger**: The workflow can be manually triggered from the Actions tab.

### What it does

1. Clones the FPL-Elo-Insights repository for additional data
2. Fetches fresh data from the official FPL API
3. Merges the data sources
4. Updates the MySQL database with fresh player statistics
5. Logs the ingestion run for monitoring

### Monitoring

- Check the Actions tab for workflow runs
- Database table `ingest_runs` tracks successful ingestions
- Failed runs will be logged in GitHub Actions

### Local Testing

To test the ingestion script locally:

```bash
cd flask-api
python scripts/test_ingest.py
```

Make sure to set the correct database credentials in the test script.
