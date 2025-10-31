"""
Fetch medRxiv articles from BioModel API and medRxiv website.
"""
import os
import re
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote

import requests
import feedparser
from bs4 import BeautifulSoup

try:
    from fuzzywuzzy import fuzz
except ImportError:
    # Fallback if fuzzywuzzy not available
    class fuzz:
        @staticmethod
        def ratio(s1, s2):
            # Simple fallback: exact match
            return 100 if s1 == s2 else 0

logger = logging.getLogger(__name__)


class ArticleFetcher:
    """Fetches articles from BioModel and medRxiv."""
    
    def __init__(self, max_articles: int = 200):
        """
        Initialize article fetcher.
        
        Args:
            max_articles: Maximum number of articles to fetch
        """
        self.max_articles = max_articles
        self.biomodel_api_key = os.getenv('BIO_MODEL_API_KEY')
        self.biomodel_base_url = os.getenv('BIO_MODEL_BASE_URL', 'https://api.biomodel.example.com')
    
    def fetch_articles(
        self,
        keyword: str = "artificial intelligence",
        days: int = 30
    ) -> List[Dict]:
        """
        Fetch articles from all available sources.
        
        Args:
            keyword: Search keyword
            days: Number of days to look back
            
        Returns:
            List of standardized article dictionaries
        """
        articles = []
        
        # Try BioModel first
        if self.biomodel_api_key:
            try:
                biomodel_articles = self._fetch_from_biomodel(keyword, days)
                articles.extend(biomodel_articles)
                logger.info(f"Fetched {len(biomodel_articles)} articles from BioModel")
            except Exception as e:
                logger.warning(f"BioModel fetch failed: {e}")
        
        # Fetch from medRxiv
        try:
            medrxiv_articles = self._fetch_from_medrxiv(keyword, days)
            articles.extend(medrxiv_articles)
            logger.info(f"Fetched {len(medrxiv_articles)} articles from medRxiv")
        except Exception as e:
            logger.warning(f"medRxiv fetch failed: {e}")
        
        # Deduplicate
        deduplicated = self._deduplicate_articles(articles)
        logger.info(f"After deduplication: {len(deduplicated)} articles")
        
        # Limit to max_articles
        return deduplicated[:self.max_articles]
    
    def _fetch_from_biomodel(self, keyword: str, days: int) -> List[Dict]:
        """
        Fetch from BioModel API.
        
        Note: This is a placeholder implementation as the actual BioModel API
        specification is not provided. Adjust based on actual API.
        """
        articles = []
        
        # Check if URL is configured and not the default placeholder
        if self.biomodel_base_url == 'https://api.biomodel.example.com':
            logger.warning(
                "BioModel API URL is not configured (using placeholder). "
                "Set BIO_MODEL_BASE_URL environment variable to use BioModel API."
            )
            return articles
        
        # Construct API URL
        base_url = f"{self.biomodel_base_url}/search"
        
        params = {
            'query': keyword,
            'days': days,
            'source': 'medrxiv',
            'limit': self.max_articles
        }
        
        headers = {
            'Authorization': f'Bearer {self.biomodel_api_key}'
        }
        
        try:
            response = self._make_request_with_retry(
                base_url,
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response - adjust based on actual API response format
                for item in data.get('results', []):
                    article = self._parse_biomodel_article(item)
                    if article:
                        articles.append(article)
        
        except Exception as e:
            logger.error(f"BioModel API error: {e}")
            raise
        
        return articles
    
    def _parse_biomodel_article(self, item: Dict) -> Optional[Dict]:
        """Parse BioModel API response item into standardized format."""
        try:
            # Extract corresponding author
            corresponding_author = ""
            authors_list = item.get('authors', [])
            
            if isinstance(authors_list, list):
                for author in authors_list:
                    if isinstance(author, dict) and author.get('corresponding'):
                        corresponding_author = author.get('name', '')
                        break
            
            # If no explicit corresponding author, use first author
            if not corresponding_author and authors_list:
                if isinstance(authors_list[0], dict):
                    corresponding_author = authors_list[0].get('name', '')
                else:
                    corresponding_author = str(authors_list[0])
            
            return {
                'id': item.get('doi', item.get('id', '')),
                'title': item.get('title', ''),
                'authors': authors_list,
                'corresponding_author': corresponding_author,
                'affiliations': item.get('affiliations', []),
                'abstract': item.get('abstract', ''),
                'published_at': item.get('published_at', ''),
                'url': item.get('url', item.get('doi', '')),
                'source': 'biomodel'
            }
        except Exception as e:
            logger.warning(f"Failed to parse BioModel article: {e}")
            return None
    
    def _fetch_from_medrxiv(self, keyword: str, days: int) -> List[Dict]:
        """Fetch from medRxiv RSS/website."""
        articles = []
        
        # Try RSS feed first
        try:
            rss_articles = self._fetch_from_medrxiv_rss(keyword, days)
            articles.extend(rss_articles)
        except Exception as e:
            logger.warning(f"medRxiv RSS fetch failed: {e}")
        
        # Try search page if needed
        if len(articles) < 50:  # If RSS didn't return enough
            try:
                search_articles = self._fetch_from_medrxiv_search(keyword, days)
                articles.extend(search_articles)
            except Exception as e:
                logger.warning(f"medRxiv search fetch failed: {e}")
        
        return articles
    
    def _fetch_from_medrxiv_rss(self, keyword: str, days: int) -> List[Dict]:
        """Fetch from medRxiv RSS feed."""
        articles = []
        
        # medRxiv RSS feed URL
        rss_url = "https://connect.medrxiv.org/medrxiv_xml.php?subject=all"
        
        try:
            feed = feedparser.parse(rss_url)
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            for entry in feed.entries[:self.max_articles]:
                # Check if keyword in title or summary
                if keyword.lower() not in entry.title.lower() and \
                   keyword.lower() not in entry.get('summary', '').lower():
                    continue
                
                # Check date
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if pub_date < cutoff_date:
                        continue
                except:
                    pass
                
                article = self._parse_rss_entry(entry)
                if article:
                    articles.append(article)
        
        except Exception as e:
            logger.error(f"RSS parsing error: {e}")
            raise
        
        return articles
    
    def _parse_rss_entry(self, entry) -> Optional[Dict]:
        """Parse RSS entry into standardized format."""
        try:
            # Extract DOI from link
            doi = ""
            link = entry.get('link', '')
            doi_match = re.search(r'10\.\d{4,}/[^\s]+', link)
            if doi_match:
                doi = doi_match.group(0)
            
            # Parse published date
            published_at = ""
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6])
                published_at = pub_date.isoformat()
            
            return {
                'id': doi or link,
                'title': entry.get('title', ''),
                'authors': self._parse_authors_from_rss(entry),
                'corresponding_author': '',  # Not available in RSS
                'affiliations': [],
                'abstract': entry.get('summary', ''),
                'published_at': published_at,
                'url': link,
                'source': 'medrxiv'
            }
        except Exception as e:
            logger.warning(f"Failed to parse RSS entry: {e}")
            return None
    
    def _parse_authors_from_rss(self, entry) -> List[str]:
        """Parse authors from RSS entry."""
        authors = []
        
        if hasattr(entry, 'authors'):
            for author in entry.authors:
                if hasattr(author, 'name'):
                    authors.append(author.name)
        elif hasattr(entry, 'author'):
            authors.append(entry.author)
        
        return authors
    
    def _fetch_from_medrxiv_search(self, keyword: str, days: int) -> List[Dict]:
        """Fetch from medRxiv search page."""
        articles = []
        
        # Construct search URL
        search_url = f"https://www.medrxiv.org/search/{quote(keyword)}"
        
        params = {
            'limit': min(self.max_articles, 100),
            'jcode': 'medrxiv',
            'format_result': 'standard'
        }
        
        try:
            response = self._make_request_with_retry(search_url, params=params)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find article entries
                article_divs = soup.find_all('div', class_='highwire-article-citation')
                
                for div in article_divs[:self.max_articles]:
                    article = self._parse_search_result(div)
                    if article:
                        articles.append(article)
        
        except Exception as e:
            logger.error(f"Search page parsing error: {e}")
        
        return articles
    
    def _parse_search_result(self, div) -> Optional[Dict]:
        """Parse search result div into standardized format."""
        try:
            title_elem = div.find('span', class_='highwire-cite-title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            authors_elem = div.find('span', class_='highwire-citation-authors')
            authors = []
            if authors_elem:
                author_links = authors_elem.find_all('a')
                authors = [a.get_text(strip=True) for a in author_links]
            
            link_elem = div.find('a', class_='highwire-cite-linked-title')
            url = ''
            if link_elem and link_elem.get('href'):
                url = 'https://www.medrxiv.org' + link_elem['href']
            
            # Extract DOI from URL
            doi = ''
            if url:
                doi_match = re.search(r'10\.\d{4,}/[^\s]+', url)
                if doi_match:
                    doi = doi_match.group(0)
            
            return {
                'id': doi or url,
                'title': title,
                'authors': authors,
                'corresponding_author': '',
                'affiliations': [],
                'abstract': '',  # Need to fetch full page for abstract
                'published_at': '',
                'url': url,
                'source': 'medrxiv'
            }
        except Exception as e:
            logger.warning(f"Failed to parse search result: {e}")
            return None
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Deduplicate articles based on DOI, URL, or fuzzy title matching.
        
        Priority: biomodel > medrxiv > other
        """
        seen = {}
        deduplicated = []
        
        # Sort by source priority
        source_priority = {'biomodel': 0, 'medrxiv': 1, 'other': 2}
        articles_sorted = sorted(
            articles,
            key=lambda x: source_priority.get(x.get('source', 'other'), 2)
        )
        
        for article in articles_sorted:
            # Create key for deduplication
            doi = article.get('id', '')
            url = article.get('url', '')
            title = article.get('title', '')
            
            # Normalize title for fuzzy matching
            title_normalized = self._normalize_title(title)
            
            # Check if already seen
            found_duplicate = False
            
            # Check by DOI
            if doi:
                if doi in seen:
                    found_duplicate = True
                else:
                    seen[doi] = article
            
            # Check by URL
            if not found_duplicate and url:
                if url in seen:
                    found_duplicate = True
                else:
                    seen[url] = article
            
            # Check by fuzzy title matching
            if not found_duplicate and title:
                for existing_title in [a.get('title', '') for a in deduplicated]:
                    existing_normalized = self._normalize_title(existing_title)
                    similarity = fuzz.ratio(title_normalized, existing_normalized)
                    if similarity > 90:  # 90% similarity threshold
                        found_duplicate = True
                        break
            
            if not found_duplicate:
                deduplicated.append(article)
        
        return deduplicated
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for fuzzy matching."""
        # Remove punctuation and convert to lowercase
        normalized = re.sub(r'[^\w\s]', '', title.lower())
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def _make_request_with_retry(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        max_retries: int = 5,
        initial_delay: float = 1.0
    ) -> requests.Response:
        """
        Make HTTP request with exponential backoff retry.
        
        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            max_retries: Maximum retry attempts
            initial_delay: Initial delay in seconds
            
        Returns:
            Response object
            
        Raises:
            Exception: If all retries fail
        """
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response
                
                # Retry on server errors and rate limiting
                if response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Request returned {response.status_code}, "
                            f"retrying after {delay}s"
                        )
                        time.sleep(delay)
                        delay = min(delay * 2, 32)
                        continue
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(f"Request failed: {e}, retrying after {delay}s")
                    time.sleep(delay)
                    delay = min(delay * 2, 32)
                else:
                    raise Exception(
                        f"Request failed after {max_retries} attempts"
                    ) from e
        
        raise Exception(
            f"Request failed after {max_retries} attempts"
        ) from last_exception
