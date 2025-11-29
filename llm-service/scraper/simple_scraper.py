"""
Simple direct scraper - bypasses Scrapy for testing
Directly scrapes a few FPL Scout articles to verify the concept works
"""
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
from datetime import datetime


def scrape_fpl_scout_simple():
    """Simple scraper for FPL Scout"""
    print("🕷️  Simple FPL Scout Scraper")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    # Output directory
    output_dir = Path(__file__).parent / 'data' / 'raw' / 'scraped'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get the tips page
    tips_url = 'https://www.fantasyfootballscout.co.uk/fantasy-football-tips/'
    
    print(f"\n📡 Fetching: {tips_url}")
    response = requests.get(tips_url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch page: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find article links
    article_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text(strip=True)
        
        # Look for FPL-related articles
        if ('gameweek' in text.lower() or 'captain' in text.lower() or 
            'transfer' in text.lower() or 'gw' in text.lower()):
            if href.startswith('http'):
                article_links.append((href, text))
    
    # Remove duplicates
    article_links = list(dict.fromkeys(article_links))[:5]  # Get first 5 unique
    
    print(f"\n✅ Found {len(article_links)} article links")
    
    articles_saved = 0
    
    for url, title in article_links:
        print(f"\n📰 Scraping: {title[:60]}...")
        
        try:
            # Fetch article
            article_response = requests.get(url, headers=headers, timeout=10)
            if article_response.status_code != 200:
                print(f"   ❌ Failed: {article_response.status_code}")
                continue
            
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # Extract content
            content_paragraphs = []
            for p in article_soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 20:  # Skip short paragraphs
                    content_paragraphs.append(text)
            
            content = '\n\n'.join(content_paragraphs)
            
            if len(content) < 100:
                print(f"   ⚠️  Insufficient content ({len(content)} chars)")
                continue
            
            # Extract gameweek
            gw_match = re.search(r'GW\s?(\d+)', title, re.IGNORECASE)
            gameweek = int(gw_match.group(1)) if gw_match else None
            
            # Categorize
            title_lower = title.lower()
            if 'captain' in title_lower:
                category = 'captaincy'
            elif 'transfer' in title_lower:
                category = 'transfers'
            elif 'fixture' in title_lower:
                category = 'fixtures'
            else:
                category = 'general'
            
            # Generate filename
            title_slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:50].strip('-')
            if gameweek:
                filename = f"{category}_gw{gameweek}_{title_slug}.md"
            else:
                timestamp = datetime.now().strftime('%Y%m%d')
                filename = f"{category}_{timestamp}_{title_slug}.md"
            
            filepath = output_dir / filename
            
            # Save as markdown
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('---\n')
                f.write(f"title: {title}\n")
                f.write(f"source: Fantasy Football Scout\n")
                f.write(f"url: {url}\n")
                f.write(f"category: {category}\n")
                if gameweek:
                    f.write(f"gameweek: {gameweek}\n")
                f.write(f"scraped: {datetime.now().isoformat()}\n")
                f.write('---\n\n')
                f.write(f"# {title}\n\n")
                f.write(content)
            
            articles_saved += 1
            print(f"   ✅ Saved: {filename}")
            
            # Be polite - wait between requests
            import time
            time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ Scraping complete! Saved {articles_saved} articles")
    print(f"📁 Location: {output_dir}")
    
    return articles_saved


if __name__ == '__main__':
    count = scrape_fpl_scout_simple()
    
    if count > 0:
        print("\n🎉 Success! You can now view the scraped articles:")
        print("   ls -lh llm-service/data/raw/scraped/")
    else:
        print("\n⚠️  No articles were saved. Check the output above for errors.")
