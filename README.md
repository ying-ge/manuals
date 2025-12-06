# medRxiv AI Article Harvester

Automated system for harvesting and analyzing medRxiv articles related to artificial intelligence using LLM-based extraction.

## Overview

This project automatically:
1. Fetches medRxiv articles related to "artificial intelligence" from the past 30 days
2. Extracts structured metadata including corresponding authors and affiliations
3. Uses LLM (GLM4.6 with OpenAI fallback) to extract key information from abstracts:
   - What was done (what_done)
   - AI's role in the study (ai_role)
   - Models/algorithms used
   - Data sources
   - Evaluation metrics
4. Saves results as JSON and Markdown files
5. Automatically creates a Pull Request with the results (when run in GitHub Actions)

## Features

- **Multi-source fetching**: Retrieves articles from BioModel API (if available) and medRxiv
- **Smart deduplication**: Removes duplicates based on DOI, URL, or fuzzy title matching
- **LLM-based extraction**: Uses GLM4.6 as primary LLM with OpenAI as fallback
- **Heuristic fallback**: Falls back to rule-based extraction if LLMs are unavailable
- **Caching**: Caches processed articles to avoid redundant LLM calls
- **Rate limiting**: Implements exponential backoff retry for API requests
- **Comprehensive logging**: Detailed logs for debugging and monitoring

## Setup

### Prerequisites

- Python 3.10 or higher
- Required API keys (at minimum GLM_API_KEY)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ying-ge/manuals.git
cd manuals
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Required - GLM (BigModel GLM4.6) API
GLM_API_KEY=your_glm_api_key_here
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
GLM_MODEL_NAME=glm-4.6

# Optional - Fallback LLM
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Primary data source
BIO_MODEL_API_KEY=your_biomodel_api_key_here
```

### GitHub Actions Setup

To enable automated daily harvesting:

1. Go to your repository Settings → Secrets and variables → Actions
2. Add the following repository secrets:
   - `GLM_API_KEY` (required)
   - `GLM_BASE_URL` (optional, defaults to BigModel API)
   - `GLM_MODEL_NAME` (optional, defaults to glm-4.6)
   - `OPENAI_API_KEY` (optional, for fallback)
   - `BIO_MODEL_API_KEY` (optional, for enhanced data fetching)

The workflow will run daily at 2 AM UTC and create a Pull Request with results.

## Usage

### Local Testing

Run a single harvest locally:

```bash
python tools/run_once.py
```

This will:
- Check your environment variables
- Fetch articles
- Extract structured information
- Save results to the `data/` directory

### Running Tests

Run integration tests:

```bash
python tests/test_extractor.py
```

### Manual Workflow Trigger

You can also trigger the workflow manually from GitHub:
1. Go to Actions tab
2. Select "Scrape medRxiv AI Articles"
3. Click "Run workflow"

## Output Files

Each harvest generates three files in the `data/` directory:

1. **`medrxiv-ai-{timestamp}.json`**: Complete article data with extracted information
   - All metadata (title, authors, affiliations, abstract, etc.)
   - LLM-extracted fields (what_done, ai_role, models, data_sources, metrics)
   - Review flags and raw LLM output (if parsing failed)

2. **`medrxiv-ai-{timestamp}.md`**: Human-readable Markdown report
   - Formatted for easy reading
   - Includes all key information
   - Flags articles needing manual review

3. **`medrxiv-ai-{timestamp}-summary.json`**: Statistics summary
   - Total article count
   - Source breakdown (BioModel vs medRxiv)
   - List of articles needing manual review

## Configuration

You can customize the harvester by modifying `src/harvest_medrxiv.py`:

- **Search keyword**: Change from "artificial intelligence" to other terms
- **Time window**: Adjust from 30 days to other ranges
- **Maximum articles**: Change from 200 to other limits
- **LLM concurrency**: Adjust parallel LLM requests (default: 3)
- **Rate limiting**: Modify delay between requests (default: 0.5s)

Example:

```python
harvester = MedRxivHarvester(
    keyword="machine learning",  # Changed keyword
    days=7,                       # Last 7 days instead of 30
    max_articles=100,             # Limit to 100 articles
    llm_delay=1.0                 # 1 second between LLM calls
)
```

## Project Structure

```
manuals/
├── .github/
│   └── workflows/
│       └── scrape.yml           # GitHub Actions workflow
├── src/
│   ├── glm_client.py            # GLM API client
│   ├── llm_extractor.py         # LLM extraction with fallback
│   ├── fetch_articles.py        # Article fetching from sources
│   └── harvest_medrxiv.py       # Main harvesting script
├── tests/
│   └── test_extractor.py        # Integration tests
├── tools/
│   └── run_once.py              # Local testing tool
├── data/                        # Output directory (created automatically)
├── logs/                        # Log files (created automatically)
├── .cache/                      # Processed articles cache
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## LLM Extraction Logic

The system uses a three-tier fallback approach:

1. **Primary: GLM4.6** (BigModel API)
   - Fast and cost-effective
   - Configured via GLM_API_KEY
   - Returns structured JSON with all fields

2. **Fallback: OpenAI** (ChatGPT)
   - Used if GLM fails or is unavailable
   - Configured via OPENAI_API_KEY
   - Uses gpt-3.5-turbo model

3. **Final Fallback: Heuristic**
   - Rule-based keyword extraction
   - No API required
   - Results marked as `needs_manual_review`

## API Rate Limiting

All external API calls implement exponential backoff retry:
- Initial delay: 1 second
- Maximum delay: 32 seconds
- Maximum retries: 5

## Caching

The system caches processed articles in `.cache/processed.json` to:
- Avoid redundant LLM calls
- Save API costs
- Speed up re-runs

To clear the cache:
```bash
rm .cache/processed.json
```

## Troubleshooting

### No articles found

- Check that medRxiv is accessible
- Verify the search keyword matches actual papers
- Try a longer time window (e.g., 60 days)

### LLM extraction fails

- Verify GLM_API_KEY is correct
- Check API quota/limits
- Review logs in `logs/harvest.log`
- System will fallback to heuristic extraction

### GitHub Actions workflow fails

- Check that repository secrets are configured
- Verify workflow has write permissions
- Review workflow logs in Actions tab

## Security

- **Never commit API keys** to the repository
- Use `.env` for local development (ignored by git)
- Use GitHub Secrets for CI/CD
- API keys are not logged

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python tests/test_extractor.py`
5. Submit a Pull Request

## License

See repository license file.

## Support

For issues or questions:
1. Check existing GitHub Issues
2. Review logs in `logs/harvest.log`
3. Create a new issue with details and logs