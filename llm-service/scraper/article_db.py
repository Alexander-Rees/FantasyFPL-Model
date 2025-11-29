"""
Database integration for article metadata
Stores metadata in PostgreSQL while keeping files for RAG
"""
import psycopg2
from psycopg2.extras import execute_values
import os
from pathlib import Path
from datetime import datetime
import re

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass  # python-dotenv not installed, use environment variables


class ArticleDatabase:
    """Manages article metadata in PostgreSQL"""
    
    def __init__(self, db_config=None):
        """
        Initialize database connection
        
        Args:
            db_config: Dict with keys: host, port, database, user, password
                      If None, reads from environment variables
        """
        if db_config is None:
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'fpl_db'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', '')
            }
        
        self.db_config = db_config
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.db_config)
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
    
    def save_article_metadata(self, article_data):
        """
        Save article metadata to database
        
        Args:
            article_data: Dict with keys:
                - gameweek (int)
                - title (str)
                - category (str)
                - source (str)
                - url (str)
                - file_path (str)
                - author (str, optional)
                - published_date (str/datetime, optional)
                - word_count (int, optional)
        
        Returns:
            int: Article ID if successful, None otherwise
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Parse published_date if string
            published_date = article_data.get('published_date')
            if isinstance(published_date, str):
                try:
                    published_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                except:
                    published_date = None
            
            # Insert or update (upsert on URL)
            query = """
                INSERT INTO fpl_articles 
                    (gameweek, title, category, source, url, file_path, author, 
                     published_date, word_count, scraped_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) 
                DO UPDATE SET
                    gameweek = EXCLUDED.gameweek,
                    title = EXCLUDED.title,
                    category = EXCLUDED.category,
                    file_path = EXCLUDED.file_path,
                    word_count = EXCLUDED.word_count,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """
            
            cursor.execute(query, (
                article_data['gameweek'],
                article_data['title'],
                article_data['category'],
                article_data['source'],
                article_data['url'],
                article_data['file_path'],
                article_data.get('author'),
                published_date,
                article_data.get('word_count'),
                datetime.now()
            ))
            
            article_id = cursor.fetchone()[0]
            conn.commit()
            
            return article_id
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving article metadata: {e}")
            return None
        finally:
            cursor.close()
    
    def get_articles_by_gameweek(self, gameweek):
        """Get all articles for a specific gameweek"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT id, gameweek, title, category, source, url, file_path, 
                       author, published_date, word_count, scraped_at
                FROM fpl_articles
                WHERE gameweek = %s
                ORDER BY scraped_at DESC
            """
            cursor.execute(query, (gameweek,))
            
            columns = ['id', 'gameweek', 'title', 'category', 'source', 'url', 
                      'file_path', 'author', 'published_date', 'word_count', 'scraped_at']
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        finally:
            cursor.close()
    
    def get_articles_by_category(self, category, limit=50):
        """Get articles by category"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT id, gameweek, title, category, source, url, file_path, 
                       author, published_date, word_count, scraped_at
                FROM fpl_articles
                WHERE category = %s
                ORDER BY gameweek DESC, scraped_at DESC
                LIMIT %s
            """
            cursor.execute(query, (category, limit))
            
            columns = ['id', 'gameweek', 'title', 'category', 'source', 'url', 
                      'file_path', 'author', 'published_date', 'word_count', 'scraped_at']
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        finally:
            cursor.close()
    
    def get_recent_articles(self, limit=20):
        """Get most recently scraped articles"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT id, gameweek, title, category, source, url, file_path, 
                       author, published_date, word_count, scraped_at
                FROM fpl_articles
                ORDER BY scraped_at DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            
            columns = ['id', 'gameweek', 'title', 'category', 'source', 'url', 
                      'file_path', 'author', 'published_date', 'word_count', 'scraped_at']
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        finally:
            cursor.close()
    
    def get_article_stats(self):
        """Get statistics about scraped articles"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    COUNT(*) as total_articles,
                    COUNT(DISTINCT gameweek) as gameweeks_covered,
                    COUNT(DISTINCT category) as categories,
                    MIN(gameweek) as earliest_gw,
                    MAX(gameweek) as latest_gw,
                    SUM(word_count) as total_words
                FROM fpl_articles
            """
            cursor.execute(query)
            
            row = cursor.fetchone()
            return {
                'total_articles': row[0],
                'gameweeks_covered': row[1],
                'categories': row[2],
                'earliest_gw': row[3],
                'latest_gw': row[4],
                'total_words': row[5] or 0
            }
            
        finally:
            cursor.close()


def count_words(text):
    """Count words in text"""
    if not text:
        return 0
    # Remove markdown formatting
    text = re.sub(r'[#*_`\[\]()]', '', text)
    words = text.split()
    return len(words)
