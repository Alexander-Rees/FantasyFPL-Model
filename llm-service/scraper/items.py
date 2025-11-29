"""
Scrapy Items - Data models for scraped FPL articles
"""
import scrapy


class FPLArticle(scrapy.Item):
    """Data model for FPL article"""
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    published_date = scrapy.Field()
    gameweek = scrapy.Field()  # Extracted from title/content
    category = scrapy.Field()  # captaincy, transfers, strategy, etc.
    content = scrapy.Field()   # Main article text
    tags = scrapy.Field()      # Player names, teams mentioned
    source = scrapy.Field()    # Website name
