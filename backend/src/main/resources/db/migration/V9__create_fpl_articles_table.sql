-- Create table for FPL article metadata
-- Files remain on disk for RAG, metadata in DB for querying

CREATE TABLE fpl_articles (
    id BIGSERIAL PRIMARY KEY,
    gameweek INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    category VARCHAR(50) NOT NULL,
    source VARCHAR(100) NOT NULL,
    url TEXT NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    author VARCHAR(200),
    published_date TIMESTAMP,
    scraped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    word_count INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_fpl_articles_gameweek ON fpl_articles(gameweek);
CREATE INDEX idx_fpl_articles_category ON fpl_articles(category);
CREATE INDEX idx_fpl_articles_scraped_at ON fpl_articles(scraped_at DESC);
CREATE INDEX idx_fpl_articles_gw_category ON fpl_articles(gameweek, category);

-- Comments
COMMENT ON TABLE fpl_articles IS 'Metadata for scraped FPL articles (content stored as markdown files)';
COMMENT ON COLUMN fpl_articles.file_path IS 'Relative path to markdown file from scraper root';
COMMENT ON COLUMN fpl_articles.category IS 'Article category: captaincy, transfers, fixtures, differentials, general';
COMMENT ON COLUMN fpl_articles.word_count IS 'Approximate word count for content length tracking';
