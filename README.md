# Twitter Thread Summarizer

A powerful web application that extracts and summarizes Twitter/X threads into 5 concise bullet points using AI. Built with FastAPI, Firecrawl, and LangChain.

## Features

- 🐦 **Thread Extraction**: Scrapes any public Twitter/X thread using Firecrawl API
- 🤖 **AI Summarization**: Uses OpenAI or Mistral to generate 5 key bullet points
- 🌐 **Clean Web Interface**: Simple, responsive UI for easy interaction
- ⚡ **Fast Processing**: Optimized for quick thread analysis
- 🔄 **Provider Fallback**: Automatic fallback between OpenAI and Mistral
- 📱 **Mobile Friendly**: Responsive design works on all devices

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/DP17-Studios/Xthreads-Summarizer
cd Xthread_summarizer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
# OR
MISTRAL_API_KEY=your_mistral_api_key_here
```

### 4. Run the Application
```bash
python main.py
```

Visit `http://localhost:8000` to use the application.

## API Keys Setup

### Required:
- **Firecrawl API**: Get your key from [firecrawl.dev](https://firecrawl.dev/)

### LLM Provider (choose one):
- **OpenAI API**: Get your key from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Mistral API**: Get your key from [Mistral Console](https://console.mistral.ai/api-keys/)

## Usage

1. **Enter Thread URL**: Paste any public Twitter/X thread URL
2. **Click Summarize**: The app will scrape and analyze the thread
3. **Get Summary**: Receive 5 key bullet points summarizing the thread
4. **Copy or Share**: Use the built-in copy function or view the original

### Supported URL Formats
- `https://twitter.com/username/status/1234567890123456789`
- `https://x.com/username/status/1234567890123456789`

## Project Structure

```
Xthread_summarizer/
├── main.py              # FastAPI application and routes
├── xthread_scraper.py    # Thread scraping logic using Firecrawl
├── summarizer.py        # LLM summarization using LangChain
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html       # Web interface
├── static/
│   └── style.css        # Styling
├── .env.example         # Environment variables template
├── .replit              # Replit configuration
├── replit.nix          # Nix packages for Replit
└── README.md           # This file
```

## API Endpoints

### Web Interface
- `GET /` - Main web interface
- `POST /summarize` - Process thread via form submission

### REST API
- `POST /api/summarize` - JSON endpoint for thread summarization
- `GET /health` - Health check and service status
- `GET /api/providers` - LLM provider status

### Example API Usage
```bash
curl -X POST "http://localhost:8000/api/summarize" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://twitter.com/username/status/1234567890123456789"}'
```

## Deployment

### Deploy on Replit
1. Fork this repository on Replit
2. Set up your environment variables in the Secrets tab:
   - `FIRECRAWL_API_KEY`
   - `OPENAI_API_KEY` or `MISTRAL_API_KEY`
3. Click Run

### Deploy on Other Platforms
The application is containerizable and can be deployed on:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS/GCP/Azure

Make sure to set the environment variables in your deployment platform.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FIRECRAWL_API_KEY` | Yes | Your Firecrawl API key |
| `OPENAI_API_KEY` | Optional* | Your OpenAI API key |
| `MISTRAL_API_KEY` | Optional* | Your Mistral API key |
| `PORT` | No | Server port (default: 8000) |
| `HOST` | No | Server host (default: 0.0.0.0) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

*At least one LLM provider key is required

## Error Handling

The application includes comprehensive error handling for:
- Invalid or inaccessible Twitter URLs
- API failures and rate limiting
- Network connectivity issues
- Missing or invalid API keys
- Content parsing errors

## Performance

- **Scraping**: 2-5 seconds depending on thread length
- **Summarization**: 3-8 seconds depending on content and provider
- **Total Processing**: Typically 5-15 seconds for complete analysis

## Limitations

- Only works with public Twitter/X threads
- Requires active API keys for Firecrawl and LLM providers
- Subject to API rate limits
- Thread content must be in a supported language

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

If you encounter any issues:
1. Check the `/health` endpoint for service status
2. Verify your API keys are valid
3. Ensure the Twitter thread URL is public and accessible
4. Check the application logs for detailed error messages

## Technologies Used

- **Backend**: FastAPI, Python 3.10+
- **Scraping**: Firecrawl API
- **AI/LLM**: OpenAI GPT-3.5, Mistral via LangChain
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Replit, Docker-compatible

---

**Happy Thread Summarizing! 🐦✨**
