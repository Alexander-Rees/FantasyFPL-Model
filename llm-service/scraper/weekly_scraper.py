"""
Weekly FPL Content Scraper
Organizes articles by gameweek for time-relevant RAG context
Saves metadata to PostgreSQL for queryability
"""
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
from datetime import datetime
import json
from article_db import ArticleDatabase, count_words


def get_current_gameweek():
    """
    Fetch current gameweek from FPL API
    """
    try:
        response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/', timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Find current gameweek
            for event in data['events']:
                if event['is_current']:
                    return event['id']
            # If no current, find next
            for event in data['events']:
                if event['is_next']:
                    return event['id']
        return None
    except Exception as e:
        print(f"⚠️  Could not fetch current gameweek from API: {e}")
        return None


def scrape_for_gameweek(gameweek=None, max_articles=20, save_to_db=True):
    """
    Scrape FPL articles for a specific gameweek
    
    Args:
        gameweek: Gameweek number (if None, auto-detect from API)
        max_articles: Maximum articles to scrape
        save_to_db: Whether to save metadata to PostgreSQL (default: True)
    """
    print("🕷️  Weekly FPL Content Scraper")
    print("=" * 60)
    
    # Initialize database connection if needed
    db = None
    if save_to_db:
        try:
            db = ArticleDatabase()
            db.connect()
            print("✅ Connected to PostgreSQL")
        except Exception as e:
            print(f"⚠️  Could not connect to database: {e}")
            print("   Continuing without database storage...")
            db = None
    
    # Get current gameweek if not specified
    if gameweek is None:
        gameweek = get_current_gameweek()
        if gameweek is None:
            print("❌ Could not determine current gameweek")
            if db:
                db.close()
            return 0
    
    print(f"\n🎯 Target Gameweek: GW{gameweek}")
    
    # Create gameweek-specific directory
    base_dir = Path(__file__).parent / 'data' / 'raw' / 'scraped'
    gw_dir = base_dir / f'gw{gameweek}'
    gw_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory: {gw_dir}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    # URLs to scrape
    urls_to_scrape = [
        ('https://www.fantasyfootballscout.co.uk/fantasy-football-tips/', 'FPL Scout Tips'),
        ('https://www.fantasyfootballscout.co.uk/captain-picks/', 'FPL Scout Captains'),
        ('https://www.fantasyfootballscout.co.uk/transfer-tips/', 'FPL Scout Transfers'),
    ]
    
    all_article_links = []
    
    # Collect article links from all pages
    for url, source_name in urls_to_scrape:
        print(f"\n📡 Fetching: {source_name}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Failed: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Look for gameweek-specific articles
                if f'gw{gameweek}' in text.lower() or f'gw {gameweek}' in text.lower():
                    if href.startswith('http'):
                        all_article_links.append((href, text))
                # Also look for recent general FPL content
                elif any(word in text.lower() for word in ['gameweek', 'captain', 'transfer', 'fixture']):
                    if href.startswith('http') and 'fantasyfootballscout.co.uk' in href:
                        all_article_links.append((href, text))
            
            print(f"   ✅ Found {len(all_article_links)} potential articles")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Remove duplicates and limit
    all_article_links = list(dict.fromkeys(all_article_links))[:max_articles]
    
    print(f"\n📰 Scraping {len(all_article_links)} articles for GW{gameweek}...")
    
    articles_saved = 0
    metadata = {
        'gameweek': gameweek,
        'scraped_at': datetime.now().isoformat(),
        'articles': []
    }
    
    for url, title in all_article_links:
        print(f"\n   📄 {title[:60]}...")
        
        try:
            # Fetch article
            article_response = requests.get(url, headers=headers, timeout=10)
            if article_response.status_code != 200:
                print(f"      ❌ Failed: {article_response.status_code}")
                continue
            
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # Extract content
            content_paragraphs = []
            for p in article_soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 20:
                    content_paragraphs.append(text)
            
            content = '\n\n'.join(content_paragraphs)
            
            if len(content) < 100:
                print(f"      ⚠️  Skipped (insufficient content)")
                continue
            
            # Extract gameweek from title
            gw_match = re.search(r'GW\s?(\d+)', title, re.IGNORECASE)
            article_gw = int(gw_match.group(1)) if gw_match else gameweek
            
            # Categorize
            title_lower = title.lower()
            if 'captain' in title_lower:
                category = 'captaincy'
            elif 'transfer' in title_lower:
                category = 'transfers'
            elif 'fixture' in title_lower:
                category = 'fixtures'
            elif 'differential' in title_lower:
                category = 'differentials'
            else:
                category = 'general'
            
            # Generate filename
            title_slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:50].strip('-')
            filename = f"{category}_{title_slug}.md"
            filepath = gw_dir / filename
            
            # Calculate word count
            word_count = count_words(content)
            
            # Save as markdown
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('---\n')
                f.write(f"title: {title}\n")
                f.write(f"source: Fantasy Football Scout\n")
                f.write(f"url: {url}\n")
                f.write(f"category: {category}\n")
                f.write(f"gameweek: {article_gw}\n")
                f.write(f"scraped_at: {datetime.now().isoformat()}\n")
                f.write('---\n\n')
                f.write(f"# {title}\n\n")
                f.write(content)
            
            # Save metadata to database
            if db:
                try:
                    # Relative path from scraper root
                    relative_path = f"data/raw/scraped/gw{gameweek}/{filename}"
                    
                    article_metadata = {
                        'gameweek': article_gw,
                        'title': title,
                        'category': category,
                        'source': 'Fantasy Football Scout',
                        'url': url,
                        'file_path': relative_path,
                        'word_count': word_count
                    }
                    
                    article_id = db.save_article_metadata(article_metadata)
                    if article_id:
                        print(f"      💾 Saved to DB (ID: {article_id})")
                except Exception as e:
                    print(f"      ⚠️  DB save failed: {e}")
            
            articles_saved += 1
            metadata['articles'].append({
                'filename': filename,
                'title': title,
                'category': category,
                'url': url,
                'word_count': word_count
            })
            
            print(f"      ✅ Saved")
            
            # Be polite
            import time
            time.sleep(2)
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Save metadata
    metadata_file = gw_dir / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Display database stats if connected
    if db:
        try:
            stats = db.get_article_stats()
            print(f"\n📊 Database Stats:")
            print(f"   Total articles: {stats['total_articles']}")
            print(f"   Gameweeks covered: GW{stats['earliest_gw']}-GW{stats['latest_gw']}")
            print(f"   Total words: {stats['total_words']:,}")
        except Exception as e:
            print(f"   ⚠️  Could not fetch stats: {e}")
        finally:
            db.close()
    
    print("\n" + "=" * 60)
    print(f"✅ Scraping complete for GW{gameweek}!")
    print(f"📊 Saved {articles_saved} articles")
    print(f"📁 Files: {gw_dir}")
    if db:
        print(f"💾 Metadata: PostgreSQL (fpl_articles table)")
    
    return articles_saved


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Weekly FPL content scraper')
    parser.add_argument(
        '--gameweek',
        type=int,
        help='Gameweek to scrape (default: auto-detect current)',
        default=None
    )
    parser.add_argument(
        '--max-articles',
        type=int,
        help='Maximum articles to scrape (default: 20)',
        default=20
    )
    
    args = parser.parse_args()
    
    count = scrape_for_gameweek(
        gameweek=args.gameweek,
        max_articles=args.max_articles
    )
    
    if count > 0:
        print("\n🎉 Success! View articles:")
        if args.gameweek:
            print(f"   ls -lh llm-service/scraper/data/raw/scraped/gw{args.gameweek}/")
        else:
            print("   ls -lh llm-service/scraper/data/raw/scraped/gw*/")
    else:
        print("\n⚠️  No articles were saved.")
