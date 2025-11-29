"""
Test script to verify scraper functionality
Tests individual components before running full scrape
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup


def test_website_access():
    """Test if we can access FPL websites"""
    print("🧪 Testing Website Access")
    print("=" * 60)
    
    test_urls = [
        ('FPL Scout', 'https://www.fantasyfootballscout.co.uk/'),
        ('FPL Wire', 'https://www.fplwire.com/'),
    ]
    
    headers = {
        'User-Agent': 'FPL-Assistant-Bot/1.0 (Educational/Personal Use)'
    }
    
    for name, url in test_urls:
        try:
            print(f"\n📡 Testing {name}...")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ {name} is accessible")
                
                # Check for content
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all(['article', 'h2', 'h3'])
                print(f"   Found {len(articles)} potential article elements")
            else:
                print(f"   ❌ {name} returned status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error accessing {name}: {e}")
    
    print("\n" + "=" * 60)


def test_robots_txt():
    """Check robots.txt to see if scraping is allowed"""
    print("\n🤖 Testing robots.txt")
    print("=" * 60)
    
    sites = [
        ('FPL Scout', 'https://www.fantasyfootballscout.co.uk/robots.txt'),
        ('FPL Wire', 'https://www.fplwire.com/robots.txt'),
    ]
    
    for name, url in sites:
        try:
            print(f"\n📄 {name} robots.txt:")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(response.text[:500])  # First 500 chars
            else:
                print(f"   No robots.txt found (status {response.status_code})")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 60)


def test_article_extraction():
    """Test extracting a single article"""
    print("\n📰 Testing Article Extraction")
    print("=" * 60)
    
    # Try to get a recent article from FPL Scout
    test_url = 'https://www.fantasyfootballscout.co.uk/fantasy-football-tips/'
    
    headers = {
        'User-Agent': 'FPL-Assistant-Bot/1.0 (Educational/Personal Use)'
    }
    
    try:
        print(f"\n🔍 Fetching: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different selectors
            selectors = [
                ('article h2 a', 'Article H2 links'),
                ('article h3 a', 'Article H3 links'),
                ('.post-title a', 'Post title links'),
                ('h2.entry-title a', 'Entry title links'),
            ]
            
            for selector, description in selectors:
                links = soup.select(selector)
                if links:
                    print(f"\n✅ Found {len(links)} links using: {description}")
                    print(f"   First link: {links[0].get('href', 'No href')}")
                    print(f"   First title: {links[0].get_text(strip=True)[:60]}...")
                    break
            else:
                print("\n❌ No article links found with any selector")
                print("   Page title:", soup.find('title').get_text() if soup.find('title') else 'No title')
        else:
            print(f"❌ Failed to fetch page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)


def test_scraper_pipeline():
    """Test the scraper pipeline"""
    print("\n⚙️  Testing Scraper Pipeline")
    print("=" * 60)
    
    from scraper.items import FPLArticle
    from scraper.pipelines import FPLScraperPipeline
    
    # Create a test article
    test_article = FPLArticle()
    test_article['title'] = 'GW12 Captain Picks Test'
    test_article['source'] = 'Test Source'
    test_article['url'] = 'https://example.com/test'
    test_article['category'] = 'captaincy'
    test_article['gameweek'] = 12
    test_article['content'] = 'This is a test article content. ' * 20  # Make it long enough
    test_article['author'] = 'Test Author'
    test_article['published_date'] = '2024-11-21'
    test_article['tags'] = ['Haaland', 'Salah']
    
    # Test pipeline
    class MockSpider:
        def __init__(self):
            self.logger = self
        
        def info(self, msg):
            print(f"   {msg}")
        
        def warning(self, msg):
            print(f"   ⚠️  {msg}")
        
        def error(self, msg):
            print(f"   ❌ {msg}")
    
    pipeline = FPLScraperPipeline()
    spider = MockSpider()
    
    print("\n📝 Testing pipeline with mock article...")
    pipeline.open_spider(spider)
    result = pipeline.process_item(test_article, spider)
    pipeline.close_spider(spider)
    
    # Check if file was created
    output_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'scraped'
    files = list(output_dir.glob('*.md'))
    
    if files:
        print(f"\n✅ Pipeline test successful!")
        print(f"   Created file: {files[-1].name}")
        
        # Show file content
        with open(files[-1], 'r') as f:
            content = f.read()
            print(f"\n   File preview:")
            print("   " + "\n   ".join(content.split('\n')[:15]))
    else:
        print("\n❌ No files created by pipeline")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    print("\n🕷️  FPL Scraper Test Suite")
    print("=" * 60)
    
    test_website_access()
    test_robots_txt()
    test_article_extraction()
    test_scraper_pipeline()
    
    print("\n✅ All tests complete!")
    print("\nIf all tests passed, you can run the full scraper with:")
    print("  python run_scraper.py --spider fpl_scout")
