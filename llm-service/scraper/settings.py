"""
Scrapy Settings - Ethical scraping configuration
"""

# Scrapy settings for FPL scraper
BOT_NAME = 'fpl_scraper'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 1  # Be polite - one request at a time

# Configure a delay for requests (in seconds)
DOWNLOAD_DELAY = 3  # 3 seconds between requests

# Disable cookies (not needed for public content)
COOKIES_ENABLED = False

# Disable Telemetry
TELNETCONSOLE_ENABLED = False

# User-Agent
USER_AGENT = 'FPL-Assistant-Bot/1.0 (Educational/Personal Use; +https://github.com/Alexander-Rees/FantasyFPL-Model)'

# Configure item pipelines
ITEM_PIPELINES = {
    'scraper.pipelines.FPLScraperPipeline': 300,
}

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 3
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 1 day
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404]

# Log level
LOG_LEVEL = 'INFO'
