"""
FPL Wire Spider
Scrapes strategy articles and weekly tips
"""
import scrapy
from scraper.items import FPLArticle
import re


class FPLWireSpider(scrapy.Spider):
    name = 'fpl_wire'
    allowed_domains = ['fplwire.com']
    
    start_urls = [
        'https://www.fplwire.com/articles/',
    ]
    
    custom_settings = {
        'DEPTH_LIMIT': 2,
    }
    
    def parse(self, response):
        """Parse article listing pages"""
        self.logger.info(f"Parsing: {response.url}")
        
        # Extract article links
        article_links = response.css('article h2 a::attr(href), .post-title a::attr(href)').getall()
        
        if not article_links:
            self.logger.warning(f"No article links found on {response.url}")
            return
        
        for article_link in article_links[:10]:
            yield response.follow(article_link, self.parse_article)
        
        # Pagination
        next_page = response.css('a.next::attr(href), .pagination a.next::attr(href)').get()
        if next_page and response.meta.get('depth', 0) < 1:
            yield response.follow(next_page, self.parse)
    
    def parse_article(self, response):
        """Parse individual article"""
        article = FPLArticle()
        
        article['url'] = response.url
        article['source'] = 'FPL Wire'
        
        # Title
        title = response.css('h1::text, h1.entry-title::text').get()
        article['title'] = title.strip() if title else 'Untitled'
        
        # Author
        author = response.css('.author::text, [rel="author"]::text').get()
        article['author'] = author.strip() if author else None
        
        # Date
        pub_date = response.css('time::attr(datetime), .published::attr(datetime)').get()
        article['published_date'] = pub_date
        
        # Gameweek
        gw_match = re.search(r'GW\s?(\d+)', article['title'], re.IGNORECASE)
        article['gameweek'] = int(gw_match.group(1)) if gw_match else None
        
        # Category
        article['category'] = self.categorize_article(article['title'], response.url)
        
        # Content
        content_paragraphs = response.css('article p::text, .entry-content p::text').getall()
        article['content'] = '\n\n'.join([p.strip() for p in content_paragraphs if p.strip()])
        
        # Tags
        tags = response.css('.tags a::text, a[rel="tag"]::text').getall()
        article['tags'] = [tag.strip() for tag in tags if tag.strip()]
        
        if len(article['content']) > 100:
            yield article
    
    def categorize_article(self, title, url):
        """Categorize article"""
        title_lower = title.lower()
        url_lower = url.lower()
        
        if 'captain' in title_lower:
            return 'captaincy'
        elif 'transfer' in title_lower:
            return 'transfers'
        elif any(word in title_lower for word in ['wildcard', 'chip', 'strategy']):
            return 'strategy'
        elif 'fixture' in title_lower:
            return 'fixtures'
        else:
            return 'general'
