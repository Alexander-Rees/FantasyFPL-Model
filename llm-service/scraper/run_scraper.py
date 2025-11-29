"""
Main script to run all FPL scrapers
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import scraper modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.fpl_scout_spider import FPLScoutSpider
from spiders.fpl_wire_spider import FPLWireSpider


def run_all_scrapers():
    """Run all FPL scrapers"""
    print("🕷️  Starting FPL Content Scraper...")
    print("=" * 60)
    
    # Get Scrapy settings
    settings = get_project_settings()
    
    # Override settings from our settings.py
    from scraper import settings as scraper_settings
    for key in dir(scraper_settings):
        if key.isupper():
            settings.set(key, getattr(scraper_settings, key))
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Add spiders
    print("\n📰 Scraping Fantasy Football Scout...")
    process.crawl(FPLScoutSpider)
    
    print("📰 Scraping FPL Wire...")
    process.crawl(FPLWireSpider)
    
    # Start crawling
    print("\n🚀 Starting crawl...\n")
    process.start()
    
    print("\n" + "=" * 60)
    print("✅ Scraping complete!")
    print(f"📁 Articles saved to: llm-service/data/raw/scraped/")


def run_single_scraper(spider_name):
    """Run a single spider by name"""
    spiders = {
        'fpl_scout': FPLScoutSpider,
        'fpl_wire': FPLWireSpider,
    }
    
    if spider_name not in spiders:
        print(f"❌ Unknown spider: {spider_name}")
        print(f"Available spiders: {', '.join(spiders.keys())}")
        return
    
    print(f"🕷️  Running {spider_name}...")
    
    settings = get_project_settings()
    from scraper import settings as scraper_settings
    for key in dir(scraper_settings):
        if key.isupper():
            settings.set(key, getattr(scraper_settings, key))
    
    process = CrawlerProcess(settings)
    process.crawl(spiders[spider_name])
    process.start()
    
    print(f"\n✅ {spider_name} complete!")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run FPL content scrapers')
    parser.add_argument(
        '--spider',
        type=str,
        help='Run a specific spider (fpl_scout, fpl_wire)',
        default=None
    )
    
    args = parser.parse_args()
    
    if args.spider:
        run_single_scraper(args.spider)
    else:
        run_all_scrapers()
