"""
Fantasy Football Scout Spider
Scrapes captain picks, transfer tips, and strategy articles
"""
import scrapy
from scraper.items import FPLArticle
import re
from datetime import datetime


class FPLScoutSpider(scrapy.Spider):
    name = 'fpl_scout'
    allowed_domains = ['fantasyfootballscout.co.uk']
    
    # Start with recent articles
    start_urls = [
        'https://www.fantasyfootballscout.co.uk/fantasy-football-tips/',
        'https://www.fantasyfootballscout.co.uk/captain-picks/',
        'https://www.fantasyfootballscout.co.uk/transfer-tips/',
    ]
    
    custom_settings = {
        'DEPTH_LIMIT': 2,  # Limit crawl depth
    }
    
    def parse(self, response):
        """Parse article listing pages"""
        self.logger.info(f"Parsing: {response.url}")
        
        # Extract article links - try multiple selectors
        article_selectors = [
            'article h2 a::attr(href)',
            'article h3 a::attr(href)',
            '.post-title a::attr(href)',
            'h2.entry-title a::attr(href)',
        ]
        
        article_links = []
        for selector in article_selectors:
            links = response.css(selector).getall()
            if links:
                article_links.extend(links)
                break
        
        if not article_links:
            self.logger.warning(f"No article links found on {response.url}")
            return
        
        # Follow article links
        for article_link in article_links[:10]:  # Limit to 10 articles per page
            yield response.follow(article_link, self.parse_article)
        
        # Pagination - limit to first 2 pages
        next_page = response.css('a.next::attr(href)').get()
        if next_page and response.meta.get('depth', 0) < 1:
            yield response.follow(next_page, self.parse)
    
    def parse_article(self, response):
        """Parse individual article page"""
        article = FPLArticle()
        
        # Basic metadata
        article['url'] = response.url
        article['source'] = 'Fantasy Football Scout'
        
        # Title - try multiple selectors
        title = (
            response.css('h1.entry-title::text').get() or
            response.css('h1::text').get() or
            response.css('title::text').get()
        )
        article['title'] = title.strip() if title else 'Untitled'
        
        # Author
        author = (
            response.css('span.author::text').get() or
            response.css('.author-name::text').get() or
            response.css('[rel="author"]::text').get()
        )
        article['author'] = author.strip() if author else None
        
        # Published date
        pub_date = (
            response.css('time::attr(datetime)').get() or
            response.css('.published::attr(datetime)').get() or
            response.css('.entry-date::attr(datetime)').get()
        )
        article['published_date'] = pub_date
        
        # Extract gameweek from title
        gw_match = re.search(r'GW\s?(\d+)', article['title'], re.IGNORECASE)
        article['gameweek'] = int(gw_match.group(1)) if gw_match else None
        
        # Categorize article based on title/URL
        article['category'] = self.categorize_article(article['title'], response.url)
        
        # Extract content - try multiple selectors
        content_selectors = [
            'div.entry-content p::text',
            'article p::text',
            '.post-content p::text',
            '.article-body p::text',
        ]
        
        content_paragraphs = []
        for selector in content_selectors:
            paragraphs = response.css(selector).getall()
            if paragraphs:
                content_paragraphs = paragraphs
                break
        
        if content_paragraphs:
            article['content'] = '\n\n'.join([p.strip() for p in content_paragraphs if p.strip()])
        else:
            self.logger.warning(f"No content found for {response.url}")
            article['content'] = ""
        
        # Extract tags
        tags = response.css('a.tag::text, .tags a::text').getall()
        article['tags'] = [tag.strip() for tag in tags if tag.strip()]
        
        # Only yield if we have meaningful content
        if len(article['content']) > 100:
            yield article
        else:
            self.logger.warning(f"Skipping article with insufficient content: {article['title']}")
    
    def categorize_article(self, title, url):
        """Categorize article based on title and URL"""
        title_lower = title.lower()
        url_lower = url.lower()
        
        if 'captain' in title_lower or 'captain' in url_lower:
            return 'captaincy'
        elif 'transfer' in title_lower or 'transfer' in url_lower:
            return 'transfers'
        elif any(word in title_lower for word in ['wildcard', 'chip', 'bench boost', 'triple captain', 'free hit']):
            return 'strategy'
        elif 'fixture' in title_lower or 'fixture' in url_lower:
            return 'fixtures'
        elif 'differential' in title_lower:
            return 'differentials'
        else:
            return 'general'
