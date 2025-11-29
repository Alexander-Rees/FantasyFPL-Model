"""
Query utility for FPL articles database
Demonstrates how to query article metadata
"""
from article_db import ArticleDatabase
import sys


def main():
    """Interactive query tool"""
    db = ArticleDatabase()
    
    try:
        db.connect()
        print("✅ Connected to PostgreSQL\n")
        
        # Display stats
        print("📊 Article Database Stats")
        print("=" * 60)
        stats = db.get_article_stats()
        print(f"Total articles: {stats['total_articles']}")
        print(f"Gameweeks covered: GW{stats['earliest_gw']} - GW{stats['latest_gw']}")
        print(f"Total words: {stats['total_words']:,}")
        print()
        
        # Show recent articles
        print("📰 Recent Articles (Last 10)")
        print("=" * 60)
        recent = db.get_recent_articles(limit=10)
        for article in recent:
            print(f"GW{article['gameweek']} | {article['category']:12} | {article['title'][:50]}")
        print()
        
        # Interactive queries
        while True:
            print("\nQuery Options:")
            print("1. Articles by gameweek")
            print("2. Articles by category")
            print("3. Recent articles")
            print("4. Database stats")
            print("5. Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == '1':
                gw = input("Enter gameweek number: ").strip()
                try:
                    gw = int(gw)
                    articles = db.get_articles_by_gameweek(gw)
                    print(f"\n📰 Articles for GW{gw} ({len(articles)} found)")
                    print("=" * 60)
                    for article in articles:
                        print(f"{article['category']:12} | {article['title']}")
                        print(f"   File: {article['file_path']}")
                        print(f"   Words: {article['word_count']}")
                        print()
                except ValueError:
                    print("❌ Invalid gameweek number")
            
            elif choice == '2':
                print("\nCategories: captaincy, transfers, fixtures, differentials, general")
                category = input("Enter category: ").strip()
                articles = db.get_articles_by_category(category, limit=20)
                print(f"\n📰 {category.title()} Articles ({len(articles)} found)")
                print("=" * 60)
                for article in articles:
                    print(f"GW{article['gameweek']} | {article['title'][:60]}")
                print()
            
            elif choice == '3':
                limit = input("How many articles? (default: 10): ").strip()
                limit = int(limit) if limit else 10
                articles = db.get_recent_articles(limit=limit)
                print(f"\n📰 Recent Articles ({len(articles)} found)")
                print("=" * 60)
                for article in articles:
                    print(f"GW{article['gameweek']} | {article['category']:12} | {article['title'][:50]}")
                print()
            
            elif choice == '4':
                stats = db.get_article_stats()
                print("\n📊 Database Stats")
                print("=" * 60)
                print(f"Total articles: {stats['total_articles']}")
                print(f"Gameweeks covered: {stats['gameweeks_covered']}")
                print(f"Categories: {stats['categories']}")
                print(f"Earliest GW: {stats['earliest_gw']}")
                print(f"Latest GW: {stats['latest_gw']}")
                print(f"Total words: {stats['total_words']:,}")
                print()
            
            elif choice == '5':
                break
            
            else:
                print("❌ Invalid choice")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        print("\n✅ Disconnected from database")


if __name__ == '__main__':
    main()
