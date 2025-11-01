"""
Fetch articles from multiple sources: medRxiv, PubMed, bioRxiv, and arXiv.
"""
import os
import re
import time
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote, urlencode

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
        days: int = 30,
        year: Optional[int] = None
    ) -> List[Dict]:
        """
        Fetch articles from all available sources.
        
        Args:
            keyword: Search keyword
            days: Number of days to look back (ignored if year is specified)
            year: Filter by publication year (e.g., 2025)
            
        Returns:
            List of standardized article dictionaries
        """
        articles = []
        
        # If year is specified, only fetch from that year
        if year:
            logger.info(f"Filtering for articles published in {year}")
            days = None  # Ignore days parameter when year is specified
        
        # Try BioModel first
        if self.biomodel_api_key:
            try:
                biomodel_articles = self._fetch_from_biomodel(keyword, days, year)
                articles.extend(biomodel_articles)
                logger.info(f"Fetched {len(biomodel_articles)} articles from BioModel")
            except Exception as e:
                logger.warning(f"BioModel fetch failed: {e}")
        
        # Fetch from medRxiv
        try:
            medrxiv_articles = self._fetch_from_medrxiv(keyword, days, year)
            articles.extend(medrxiv_articles)
            logger.info(f"Fetched {len(medrxiv_articles)} articles from medRxiv")
        except Exception as e:
            logger.warning(f"medRxiv fetch failed: {e}")
        
        # Fetch from bioRxiv
        try:
            biorxiv_articles = self._fetch_from_biorxiv(keyword, days, year)
            articles.extend(biorxiv_articles)
            logger.info(f"Fetched {len(biorxiv_articles)} articles from bioRxiv")
        except Exception as e:
            logger.warning(f"bioRxiv fetch failed: {e}")
        
        # Fetch from PubMed
        try:
            pubmed_articles = self._fetch_from_pubmed(keyword, days, year)
            articles.extend(pubmed_articles)
            logger.info(f"Fetched {len(pubmed_articles)} articles from PubMed")
        except Exception as e:
            logger.warning(f"PubMed fetch failed: {e}")
        
        # Fetch from arXiv (biomedical categories)
        try:
            arxiv_articles = self._fetch_from_arxiv(keyword, days, year)
            articles.extend(arxiv_articles)
            logger.info(f"Fetched {len(arxiv_articles)} articles from arXiv")
        except Exception as e:
            logger.warning(f"arXiv fetch failed: {e}")
        
        # Deduplicate
        deduplicated = self._deduplicate_articles(articles)
        logger.info(f"After deduplication: {len(deduplicated)} articles")
        
        # Filter by year if specified
        if year:
            deduplicated = [
                a for a in deduplicated 
                if self._article_in_year(a, year)
            ]
            logger.info(f"After year {year} filtering: {len(deduplicated)} articles")
        
        # Limit to max_articles
        return deduplicated[:self.max_articles]
    
    def _article_in_year(self, article: Dict, year: int) -> bool:
        """Check if article was published in the specified year."""
        published_at = article.get('published_at', '')
        if not published_at:
            return False
        
        # Try to extract year from various date formats
        year_match = re.search(r'\b(\d{4})\b', str(published_at))
        if year_match:
            return int(year_match.group(1)) == year
        
        return False
    
    def _extract_last_corresponding_author(self, authors: List, affiliations: List) -> tuple:
        """
        Extract the last corresponding author and their affiliation.
        
        Args:
            authors: List of author dicts or strings
            affiliations: List of affiliation strings or dicts
            
        Returns:
            Tuple of (author_name, affiliation)
        """
        corresponding_authors = []
        
        # Find all corresponding authors
        if isinstance(authors, list):
            for i, author in enumerate(authors):
                is_corresponding = False
                if isinstance(author, dict):
                    is_corresponding = author.get('corresponding', False) or author.get('corresponding_author', False)
                    author_name = author.get('name', '') or author.get('lastname', '') + ' ' + author.get('firstname', '')
                else:
                    author_name = str(author)
                    # Check if marked as corresponding in name
                    is_corresponding = '*' in str(author) or '(corresponding)' in str(author).lower()
                
                if is_corresponding and author_name:
                    corresponding_authors.append((i, author_name))
        
        # If no explicit corresponding author found, use last author
        if not corresponding_authors:
            if authors:
                last_author = authors[-1]
                if isinstance(last_author, dict):
                    author_name = last_author.get('name', '') or last_author.get('lastname', '') + ' ' + last_author.get('firstname', '')
                else:
                    author_name = str(last_author).strip('*').strip()
                corresponding_authors = [(-1, author_name)]
            else:
                return ('', '')
        
        # Get the last corresponding author
        last_corresponding = corresponding_authors[-1]
        author_name = last_corresponding[1].strip('*').strip()
        
        # Try to find affiliation
        affiliation = ''
        if isinstance(affiliations, list) and affiliations:
            # If author index is available, try to match
            if last_corresponding[0] >= 0 and last_corresponding[0] < len(affiliations):
                aff = affiliations[last_corresponding[0]]
                if isinstance(aff, dict):
                    affiliation = aff.get('name', '') or aff.get('institution', '')
                else:
                    affiliation = str(aff)
            else:
                # Use last affiliation as fallback
                last_aff = affiliations[-1]
                if isinstance(last_aff, dict):
                    affiliation = last_aff.get('name', '') or last_aff.get('institution', '')
                else:
                    affiliation = str(last_aff)
        
        return (author_name, affiliation)
    
    def _fetch_from_biomodel(self, keyword: str, days: Optional[int], year: Optional[int]) -> List[Dict]:
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
            
            # Extract last corresponding author
            last_corr_author, last_corr_aff = self._extract_last_corresponding_author(
                authors_list, item.get('affiliations', [])
            )
            
            return {
                'id': item.get('doi', item.get('id', '')),
                'title': item.get('title', ''),
                'authors': authors_list,
                'corresponding_author': corresponding_author,
                'last_corresponding_author': last_corr_author,
                'last_corresponding_affiliation': last_corr_aff,
                'affiliations': item.get('affiliations', []),
                'abstract': item.get('abstract', ''),
                'published_at': item.get('published_at', ''),
                'url': item.get('url', item.get('doi', '')),
                'source': 'biomodel'
            }
        except Exception as e:
            logger.warning(f"Failed to parse BioModel article: {e}")
            return None
    
    def _fetch_from_medrxiv(self, keyword: str, days: Optional[int], year: Optional[int]) -> List[Dict]:
        """Fetch from medRxiv RSS/website."""
        articles = []
        
        # Try RSS feed first
        try:
            rss_articles = self._fetch_from_medrxiv_rss(keyword, days, year)
            articles.extend(rss_articles)
        except Exception as e:
            logger.warning(f"medRxiv RSS fetch failed: {e}")
        
        # Try search page if needed
        if len(articles) < 50:  # If RSS didn't return enough
            try:
                search_articles = self._fetch_from_medrxiv_search(keyword, days, year)
                articles.extend(search_articles)
            except Exception as e:
                logger.warning(f"medRxiv search fetch failed: {e}")
        
        return articles
    
    def _fetch_from_medrxiv_rss(self, keyword: str, days: Optional[int], year: Optional[int]) -> List[Dict]:
        """Fetch from medRxiv RSS feed."""
        articles = []
        
        # medRxiv RSS feed URL
        rss_url = "https://connect.medrxiv.org/medrxiv_xml.php?subject=all"
        
        try:
            feed = feedparser.parse(rss_url)
            cutoff_date = None
            if days and not year:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            for entry in feed.entries[:self.max_articles]:
                # Check if keyword in title or summary
                if keyword.lower() not in entry.title.lower() and \
                   keyword.lower() not in entry.get('summary', '').lower():
                    continue
                
                # Check date
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if year:
                        if pub_date.year != year:
                            continue
                    elif cutoff_date and pub_date < cutoff_date:
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
            
            authors = self._parse_authors_from_rss(entry)
            last_corr_author, last_corr_aff = self._extract_last_corresponding_author(authors, [])
            
            return {
                'id': doi or link,
                'title': entry.get('title', ''),
                'authors': authors,
                'corresponding_author': last_corr_author,  # Use last author as fallback
                'last_corresponding_author': last_corr_author,
                'last_corresponding_affiliation': last_corr_aff,
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
    
    def _fetch_from_medrxiv_search(self, keyword: str, days: Optional[int], year: Optional[int]) -> List[Dict]:
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
            
            last_corr_author, last_corr_aff = self._extract_last_corresponding_author(authors, [])
            
            return {
                'id': doi or url,
                'title': title,
                'authors': authors,
                'corresponding_author': last_corr_author,
                'last_corresponding_author': last_corr_author,
                'last_corresponding_affiliation': last_corr_aff,
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
    
    def _fetch_from_biorxiv(self, keyword: str, days: Optional[int], year: Optional[int]) -> List[Dict]:
        """Fetch from bioRxiv RSS feed."""
        articles = []
        
        # bioRxiv RSS feed URL
        rss_url = "https://connect.biorxiv.org/biorxiv_xml.php?subject=all"
        
        try:
            feed = feedparser.parse(rss_url)
            cutoff_date = None
            if days and not year:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            for entry in feed.entries[:self.max_articles]:
                # Check if keyword in title or summary
                if keyword.lower() not in entry.title.lower() and \
                   keyword.lower() not in entry.get('summary', '').lower():
                    continue
                
                # Check date
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if year:
                        if pub_date.year != year:
                            continue
                    elif cutoff_date and pub_date < cutoff_date:
                        continue
                except:
                    pass
                
                article = self._parse_rss_entry(entry)
                if article:
                    article['source'] = 'biorxiv'
                    articles.append(article)
        
        except Exception as e:
            logger.error(f"bioRxiv RSS parsing error: {e}")
            raise
        
        return articles
    
    def _fetch_from_pubmed(self, keyword: str, days: Optional[int], year: Optional[int]) -> List[Dict]:
        """Fetch from PubMed using E-utilities API."""
        articles = []
        
        # PubMed E-utilities API
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
        # Build query - filter for biomedical/medical research
        query = f'({keyword}[Title/Abstract]) AND ("biology"[MeSH Terms] OR "medicine"[MeSH Terms] OR "biomedical research"[MeSH Terms])'
        if year:
            query += f' AND {year}[Publication Date]'
        elif days:
            # Calculate date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            date_str = cutoff_date.strftime('%Y/%m/%d')
            query += f' AND "{date_str}"[Publication Date] : "3000/12/31"[Publication Date]'
        
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': min(self.max_articles, 100),
            'retmode': 'json'
        }
        
        try:
            # Search for article IDs
            response = self._make_request_with_retry(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pmids = data.get('esearchresult', {}).get('idlist', [])
                
                if pmids:
                    # Fetch article details
                    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                    fetch_params = {
                        'db': 'pubmed',
                        'id': ','.join(pmids[:self.max_articles]),
                        'retmode': 'xml'
                    }
                    
                    fetch_response = self._make_request_with_retry(fetch_url, params=fetch_params)
                    
                    if fetch_response.status_code == 200:
                        articles = self._parse_pubmed_xml(fetch_response.text)
        
        except Exception as e:
            logger.error(f"PubMed API error: {e}")
            raise
        
        return articles
    
    def _parse_pubmed_xml(self, xml_content: str) -> List[Dict]:
        """Parse PubMed XML response."""
        articles = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for pubmed_article in root.findall('.//PubmedArticle'):
                try:
                    # Extract title
                    title_elem = pubmed_article.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else ''
                    
                    # Extract abstract
                    abstract_elem = pubmed_article.find('.//AbstractText')
                    abstract = abstract_elem.text if abstract_elem is not None else ''
                    
                    # Extract authors
                    authors = []
                    author_list = pubmed_article.find('.//AuthorList')
                    if author_list is not None:
                        for author in author_list.findall('Author'):
                            lastname = author.find('LastName')
                            firstname = author.find('ForeName')
                            if lastname is not None and firstname is not None:
                                authors.append(f"{firstname.text} {lastname.text}")
                    
                    # Extract affiliations
                    affiliations = []
                    affil_list = pubmed_article.findall('.//Affiliation')
                    for affil in affil_list:
                        if affil.text:
                            affiliations.append(affil.text)
                    
                    # Extract last corresponding author
                    last_corr_author, last_corr_aff = self._extract_last_corresponding_author(authors, affiliations)
                    
                    # Extract publication date
                    pub_date_elem = pubmed_article.find('.//PubDate')
                    published_at = ''
                    if pub_date_elem is not None:
                        year_elem = pub_date_elem.find('Year')
                        month_elem = pub_date_elem.find('Month')
                        day_elem = pub_date_elem.find('Day')
                        if year_elem is not None:
                            year = year_elem.text
                            month = month_elem.text if month_elem is not None else '01'
                            day = day_elem.text if day_elem is not None else '01'
                            published_at = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    
                    # Extract DOI
                    doi_elem = pubmed_article.find('.//ArticleId[@IdType="doi"]')
                    doi = doi_elem.text if doi_elem is not None else ''
                    
                    # Extract PMID
                    pmid_elem = pubmed_article.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else ''
                    
                    # Build URL
                    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}" if pmid else ''
                    
                    article = {
                        'id': doi or pmid,
                        'title': title,
                        'authors': authors,
                        'corresponding_author': last_corr_author,
                        'last_corresponding_author': last_corr_author,
                        'last_corresponding_affiliation': last_corr_aff,
                        'affiliations': affiliations,
                        'abstract': abstract,
                        'published_at': published_at,
                        'url': url,
                        'source': 'pubmed'
                    }
                    articles.append(article)
                
                except Exception as e:
                    logger.warning(f"Failed to parse PubMed article: {e}")
                    continue
        
        except ET.ParseError as e:
            logger.error(f"Failed to parse PubMed XML: {e}")
            return []
        
        return articles
    
    def _fetch_from_arxiv(self, keyword: str, days: Optional[int], year: Optional[int]) -> List[Dict]:
        """Fetch from arXiv API (biomedical categories only)."""
        articles = []
        
        # arXiv API URL - filter for biomedical categories
        # q-bio = Quantitative Biology, q-bio.BM = Biomolecules, q-bio.CB = Cell Behavior
        # cs.LG = Machine Learning (cross-list)
        base_url = "http://export.arxiv.org/api/query"
        
        # Build query - focus on biomedical + AI
        query_parts = [f'all:{keyword}']
        
        # Filter by category (biomedical)
        categories = ['q-bio.*', 'cs.LG', 'stat.ML']
        category_filter = ' OR '.join([f'cat:{cat}' for cat in categories])
        query = f'({keyword}) AND ({category_filter})'
        
        params = {
            'search_query': query,
            'start': 0,
            'max_results': min(self.max_articles, 100),
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = self._make_request_with_retry(base_url, params=params)
            
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                cutoff_date = None
                if days and not year:
                    cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                for entry in feed.entries:
                    # Check date
                    try:
                        pub_date = datetime(*entry.published_parsed[:6])
                        if year:
                            if pub_date.year != year:
                                continue
                        elif cutoff_date and pub_date < cutoff_date:
                            continue
                    except:
                        pass
                    
                    # Extract information
                    article = self._parse_arxiv_entry(entry)
                    if article:
                        articles.append(article)
        
        except Exception as e:
            logger.error(f"arXiv API error: {e}")
            raise
        
        return articles
    
    def _parse_arxiv_entry(self, entry) -> Optional[Dict]:
        """Parse arXiv entry into standardized format."""
        try:
            title = entry.get('title', '').replace('\n', ' ')
            
            # Extract authors
            authors = []
            if hasattr(entry, 'authors'):
                for author in entry.authors:
                    authors.append(author.get('name', ''))
            
            # Extract abstract
            abstract = entry.get('summary', '').replace('\n', ' ')
            
            # Extract published date
            published_at = ''
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6])
                published_at = pub_date.isoformat()
            
            # Extract ID and URL
            arxiv_id = entry.get('id', '').split('/')[-1]
            url = entry.get('link', '')
            
            # Extract last corresponding author
            last_corr_author, last_corr_aff = self._extract_last_corresponding_author(authors, [])
            
            return {
                'id': arxiv_id,
                'title': title,
                'authors': authors,
                'corresponding_author': last_corr_author,
                'last_corresponding_author': last_corr_author,
                'last_corresponding_affiliation': last_corr_aff,
                'affiliations': [],
                'abstract': abstract,
                'published_at': published_at,
                'url': url,
                'source': 'arxiv'
            }
        except Exception as e:
            logger.warning(f"Failed to parse arXiv entry: {e}")
            return None
