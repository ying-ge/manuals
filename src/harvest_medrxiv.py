"""
Main script for harvesting medRxiv articles related to AI.
"""
import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict
from pathlib import Path

try:
    from src.fetch_articles import ArticleFetcher
    from src.llm_extractor import LLMExtractor
except ImportError:
    from fetch_articles import ArticleFetcher
    from llm_extractor import LLMExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/harvest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MedRxivHarvester:
    """Main harvester for medRxiv AI articles."""
    
    def __init__(
        self,
        keyword: str = "artificial intelligence",
        days: int = 30,
        max_articles: int = 200,
        llm_concurrency: int = 3,
        llm_delay: float = 0.5
    ):
        """
        Initialize harvester.
        
        Args:
            keyword: Search keyword
            days: Number of days to look back
            max_articles: Maximum articles to fetch
            llm_concurrency: LLM request concurrency limit
            llm_delay: Delay between LLM requests in seconds
        """
        self.keyword = keyword
        self.days = days
        self.max_articles = max_articles
        self.llm_concurrency = llm_concurrency
        self.llm_delay = llm_delay
        
        self.fetcher = ArticleFetcher(max_articles=max_articles)
        self.extractor = LLMExtractor()
        
        # Cache for processed articles
        self.cache_file = Path('.cache/processed.json')
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache of processed articles."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def harvest(self) -> Dict:
        """
        Run the full harvest process.
        
        Returns:
            Dictionary with results and statistics
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        logger.info(f"Starting harvest at {timestamp}")
        
        # Step 1: Fetch articles
        logger.info(f"Fetching articles with keyword: {self.keyword}")
        articles = self.fetcher.fetch_articles(self.keyword, self.days)
        logger.info(f"Fetched {len(articles)} articles")
        
        # Step 2: Fetch full abstracts for articles that don't have them
        articles = self._enrich_articles(articles)
        
        # Step 3: Extract structured information
        logger.info("Extracting structured information from abstracts")
        processed_articles = []
        needs_review = []
        
        for i, article in enumerate(articles):
            logger.info(f"Processing article {i+1}/{len(articles)}: {article.get('title', '')[:60]}...")
            
            # Check cache
            article_id = article.get('id', '')
            if article_id in self.cache:
                logger.info(f"Using cached extraction for {article_id}")
                processed_article = self.cache[article_id]
            else:
                # Extract with LLM
                abstract = article.get('abstract', '')
                
                if not abstract or len(abstract.strip()) < 50:
                    logger.warning(f"Abstract too short or missing for article {article_id}")
                    extraction_result = {
                        'what_done': '',
                        'ai_role': '',
                        'models': '',
                        'data_sources': '',
                        'metrics': ''
                    }
                    needs_manual_review = True
                    raw_llm_output = None
                else:
                    extraction_result, needs_manual_review, raw_llm_output = self.extractor.extract(abstract)
                
                # Combine with metadata
                processed_article = {
                    **article,
                    **extraction_result,
                    'needs_manual_review': needs_manual_review,
                    'raw_llm_output': raw_llm_output
                }
                
                # Cache it
                if article_id:
                    self.cache[article_id] = processed_article
                
                # Rate limiting
                if i < len(articles) - 1:  # Don't sleep after last article
                    time.sleep(self.llm_delay)
            
            processed_articles.append(processed_article)
            
            if processed_article.get('needs_manual_review'):
                needs_review.append(article_id)
        
        # Save cache
        self._save_cache()
        
        # Step 4: Generate outputs
        logger.info("Generating output files")
        output_files = self._generate_outputs(processed_articles, timestamp, needs_review)
        
        # Step 5: Generate statistics
        stats = self._generate_statistics(processed_articles, needs_review)
        
        logger.info(f"Harvest complete. Processed {len(processed_articles)} articles")
        logger.info(f"Articles needing manual review: {len(needs_review)}")
        
        return {
            'timestamp': timestamp,
            'articles': processed_articles,
            'statistics': stats,
            'output_files': output_files,
            'needs_review': needs_review
        }
    
    def _enrich_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Enrich articles by fetching full abstracts if missing.
        
        For now, this is a placeholder. In production, you would
        fetch the full article page to get the abstract.
        """
        enriched = []
        
        for article in articles:
            # If abstract is missing or very short, try to fetch it
            if not article.get('abstract') or len(article.get('abstract', '')) < 100:
                # Placeholder - in production, fetch the full page
                logger.warning(f"Abstract missing for {article.get('title', '')[:50]}")
            
            enriched.append(article)
        
        return enriched
    
    def _generate_outputs(
        self,
        articles: List[Dict],
        timestamp: str,
        needs_review: List[str]
    ) -> Dict[str, str]:
        """
        Generate JSON and Markdown output files.
        
        Returns:
            Dictionary with output file paths
        """
        # Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        # Generate file names
        json_file = data_dir / f'medrxiv-ai-{timestamp}.json'
        md_file = data_dir / f'medrxiv-ai-{timestamp}.md'
        summary_file = data_dir / f'medrxiv-ai-{timestamp}-summary.json'
        
        # Write JSON file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON to {json_file}")
        
        # Write Markdown file
        md_content = self._generate_markdown(articles)
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        logger.info(f"Saved Markdown to {md_file}")
        
        # Write summary file
        summary = self._generate_statistics(articles, needs_review)
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved summary to {summary_file}")
        
        return {
            'json': str(json_file),
            'markdown': str(md_file),
            'summary': str(summary_file)
        }
    
    def _generate_markdown(self, articles: List[Dict]) -> str:
        """Generate Markdown report."""
        lines = [
            "# medRxiv AI Articles Report",
            "",
            f"**Generated:** {datetime.utcnow().isoformat()}Z",
            f"**Total Articles:** {len(articles)}",
            "",
            "---",
            ""
        ]
        
        for i, article in enumerate(articles, 1):
            lines.extend([
                f"## {i}. {article.get('title', 'Untitled')}",
                "",
                f"**Corresponding Author:** {article.get('corresponding_author', 'N/A')}",
                ""
            ])
            
            # Affiliations
            affiliations = article.get('affiliations', [])
            if affiliations:
                if isinstance(affiliations, list):
                    aff_str = '; '.join(str(a) for a in affiliations)
                else:
                    aff_str = str(affiliations)
                lines.append(f"**Affiliation:** {aff_str}")
                lines.append("")
            
            # Published date
            if article.get('published_at'):
                lines.append(f"**Published:** {article.get('published_at')}")
                lines.append("")
            
            # Link
            if article.get('url'):
                lines.append(f"**URL:** {article.get('url')}")
                lines.append("")
            
            # Source
            lines.append(f"**Source:** {article.get('source', 'unknown')}")
            lines.append("")
            
            # Extracted information
            lines.extend([
                "### Extracted Information",
                "",
                f"**What was done:** {article.get('what_done', 'N/A')}",
                "",
                f"**AI Role:** {article.get('ai_role', 'N/A')}",
                "",
                f"**Models:** {article.get('models', 'N/A')}",
                "",
                f"**Data Sources:** {article.get('data_sources', 'N/A')}",
                "",
                f"**Metrics:** {article.get('metrics', 'N/A')}",
                ""
            ])
            
            # Abstract excerpt
            abstract = article.get('abstract', '')
            if abstract:
                excerpt = abstract[:300] + ('...' if len(abstract) > 300 else '')
                lines.extend([
                    "### Abstract (excerpt)",
                    "",
                    excerpt,
                    ""
                ])
            
            # Review flag
            if article.get('needs_manual_review'):
                lines.extend([
                    "⚠️ **Needs Manual Review**",
                    ""
                ])
            
            lines.extend([
                "---",
                ""
            ])
        
        return '\n'.join(lines)
    
    def _generate_statistics(
        self,
        articles: List[Dict],
        needs_review: List[str]
    ) -> Dict:
        """Generate statistics summary."""
        # Count by source
        source_counts = {}
        for article in articles:
            source = article.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            'total_articles': len(articles),
            'source_breakdown': source_counts,
            'needs_manual_review': {
                'count': len(needs_review),
                'article_ids': needs_review
            },
            'execution_time': datetime.utcnow().isoformat() + 'Z'
        }


def main():
    """Main entry point."""
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    
    try:
        harvester = MedRxivHarvester()
        results = harvester.harvest()
        
        logger.info("=" * 80)
        logger.info("HARVEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total articles: {results['statistics']['total_articles']}")
        logger.info(f"Source breakdown: {results['statistics']['source_breakdown']}")
        logger.info(f"Needs review: {results['statistics']['needs_manual_review']['count']}")
        logger.info(f"Output files:")
        for key, path in results['output_files'].items():
            logger.info(f"  {key}: {path}")
        logger.info("=" * 80)
        
        return 0
    
    except Exception as e:
        logger.error(f"Harvest failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
