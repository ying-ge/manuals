# Quick Start Guide

This guide helps you get the medRxiv AI harvester running quickly.

## 1. Get Your API Keys

### Required: GLM API Key (BigModel)
1. Go to [BigModel](https://open.bigmodel.cn/)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy your API key

### Optional: OpenAI API Key (Fallback)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy your API key

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your GLM API key:

```bash
GLM_API_KEY=your_actual_api_key_here
```

## 4. Run Your First Harvest

```bash
python tools/run_once.py
```

This will:
- Fetch recent medRxiv articles about AI
- Extract key information using LLM
- Save results to `data/` directory

## 5. Check the Results

Look in the `data/` directory for:
- `medrxiv-ai-{timestamp}.json` - All data in JSON format
- `medrxiv-ai-{timestamp}.md` - Human-readable report
- `medrxiv-ai-{timestamp}-summary.json` - Quick statistics

## 6. Set Up Automated Runs (Optional)

To run automatically every day via GitHub Actions:

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Add a new secret:
   - Name: `GLM_API_KEY`
   - Value: Your GLM API key

The workflow will run daily at 2 AM UTC and create a Pull Request with results.

## Troubleshooting

### "GLM_API_KEY must be provided or set in environment"
- Make sure you created the `.env` file
- Check that `GLM_API_KEY=` has your actual key (no quotes needed)
- Verify the `.env` file is in the project root directory

### "Failed to fetch articles"
- Check your internet connection
- medRxiv might be temporarily down
- Try running again in a few minutes

### "LLM extraction failed, falling back to heuristic"
- This is normal if you don't have API keys configured
- The system will still extract information using rules
- Results will be marked as `needs_manual_review: true`

## Next Steps

- Review the full [README.md](README.md) for advanced configuration
- Check [tests/test_extractor.py](tests/test_extractor.py) for examples
- Customize search keywords in `src/harvest_medrxiv.py`

## Support

If you encounter issues:
1. Check `logs/harvest.log` for detailed error messages
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Open an issue on GitHub with the error message and log file
