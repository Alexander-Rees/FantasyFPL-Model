"""
Scrapy Pipelines - Data cleaning and storage
"""
import re
from pathlib import Path
from datetime import datetime


class FPLScraperPipeline:
    """Pipeline to clean and save scraped FPL articles"""
    
    def open_spider(self, spider):
        """Initialize output directory when spider opens"""
        self.output_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'scraped'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.articles_saved = 0
        spider.logger.info(f"Saving articles to: {self.output_dir}")
    
    def close_spider(self, spider):
        """Log statistics when spider closes"""
        spider.logger.info(f"✅ Saved {self.articles_saved} articles")
    
    def process_item(self, item, spider):
        """Process and save each scraped article"""
        # Clean content
        if item.get('content'):
            item['content'] = self.clean_text(item['content'])
        
        # Save as markdown
        filename = self.generate_filename(item)
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write YAML frontmatter
                f.write('---\n')
                f.write(f"title: {item.get('title', 'Untitled')}\n")
                f.write(f"source: {item.get('source', 'Unknown')}\n")
                f.write(f"url: {item.get('url', '')}\n")
                f.write(f"category: {item.get('category', 'general')}\n")
                
                if item.get('gameweek'):
                    f.write(f"gameweek: {item['gameweek']}\n")
                
                if item.get('author'):
                    f.write(f"author: {item['author']}\n")
                
                if item.get('published_date'):
                    f.write(f"published: {item['published_date']}\n")
                
                if item.get('tags'):
                    tags_str = ', '.join(item['tags'])
                    f.write(f"tags: [{tags_str}]\n")
                
                f.write('---\n\n')
                
                # Write content
                f.write(f"# {item.get('title', 'Untitled')}\n\n")
                f.write(item.get('content', ''))
            
            self.articles_saved += 1
            spider.logger.info(f"Saved: {filename}")
            
        except Exception as e:
            spider.logger.error(f"Error saving {filename}: {e}")
        
        return item
    
    def clean_text(self, text):
        """Clean scraped text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common promotional text
        text = re.sub(r'Subscribe to.*?(?=\n|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Sign up for.*?(?=\n|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Join our.*?(?=\n|$)', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def generate_filename(self, item):
        """Generate filename from article metadata"""
        # Create slug from title
        title = item.get('title', 'untitled')
        title_slug = re.sub(r'[^a-z0-9]+', '-', title.lower())
        title_slug = title_slug[:50]  # Limit length
        title_slug = title_slug.strip('-')
        
        # Add category and gameweek prefix
        category = item.get('category', 'general')
        
        if item.get('gameweek'):
            return f"{category}_gw{item['gameweek']}_{title_slug}.md"
        else:
            # Use timestamp for non-gameweek articles
            timestamp = datetime.now().strftime('%Y%m%d')
            return f"{category}_{timestamp}_{title_slug}.md"
