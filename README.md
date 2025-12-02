# SignalWatch 🔍

**SignalWatch** is a comprehensive Python-based tool for scanning and analyzing UK company data from Companies House (with optional OpenCorporates support). It detects name/date mismatches in filing documents and maps director-linked company networks.

## 🌟 Features

- **Data Extraction**: Fetch company profiles, filing history, and download related PDFs
- **Smart Analysis**: AI-powered OCR text extraction and name/date parsing
- **Mismatch Detection**: Compare extracted data against official records
- **Network Discovery**: Map companies through shared directors with iterative expansion
- **Rate Limit Management**: Intelligent batching (600 requests / 5 minutes)
- **Resume Capability**: Checkpoint system for interrupted scans
- **Multi-User Support**: Users can provide their own API keys
- **Web Interface**: Astra-style themed interface for easy interaction
- **Export Options**: CSV, JSON, and embeddable HTML reports

## 📋 Prerequisites

- Python 3.9+
- Companies House API Key ([Get one here](https://developer.company-information.service.gov.uk/))
- Tesseract OCR (for PDF text extraction)

### Install Tesseract OCR

**Windows:**
```powershell
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

## 🚀 Installation

1. **Clone the repository:**
```powershell
git clone https://github.com/yourusername/signalwatch.git
cd signalwatch
```

2. **Create virtual environment:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

4. **Configure environment:**
```powershell
# Copy example environment file
copy .env.example .env

# Edit .env and add your API key
notepad .env
```

5. **Setup directories:**
```powershell
python -c "from config import Config; Config.ensure_directories()"
```

## 🔑 API Key Setup

### Companies House API Key (REQUIRED)

**⚠️ You MUST provide your own API key - the application will not work without it.**

1. Register at [Companies House Developer Hub](https://developer.company-information.service.gov.uk/)
2. Create an application to get your API key
3. Enter your API key in the web interface when performing a scan

**Note:** For development/testing, you can add your key to `.env` file:
```
COMPANIES_HOUSE_API_KEY=your_key_here
```

### GitHub Token (Optional - for result caching)

SignalWatch can use GitHub as a distributed cache, sharing scan results between users to avoid duplicate API calls:

1. Create a Personal Access Token at [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Required permissions: **repo** (Full control of private repositories)
3. Add to `.env` file:
```
GITHUB_TOKEN=ghp_your_token_here
```

4. Ensure the target repo exists (default: `https://github.com/Signal-Watch/signal-watch.git`)

**Benefits:**
- ⚡ Instant results for previously scanned companies
- 💰 Reduces API usage across all users
- 📦 Automatic archiving with timestamps
- 🔄 Seamless fallback to fresh scan if cache miss

### XAI/OpenAI API Key (Required if using AI extraction)

**⚠️ Required when "Use AI Extraction" option is enabled.**

**XAI (Grok) - Recommended:**
1. Get API key from [XAI Console](https://console.x.ai/)
2. More cost-effective and faster than OpenAI
3. Enter your API key in the web interface when enabling AI extraction

**OpenAI (Alternative):**
1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to `.env` file:
```
OPENAI_API_KEY=your_openai_key_here
```

## 💻 Usage

### Web Interface

Start the web server:
```powershell
python app.py
```

Open browser: `http://localhost:5000`

### Command Line Interface

**Scan a single company:**
```powershell
python cli.py scan --company 00000006
```

**Scan multiple companies:**
```powershell
python cli.py scan --companies 00000006,00000007,00000008
```

**Scan with director network expansion:**
```powershell
python cli.py scan --company 00000006 --expand-network --max-depth 2
```

**Resume from checkpoint:**
```powershell
python cli.py resume --checkpoint-file ./data/checkpoint_20250114_120000.json
```

**Export results:**
```powershell
python cli.py export --results ./data/results.json --format csv
python cli.py export --results ./data/results.json --format html
```

## 📦 GitHub Cache Feature

SignalWatch can leverage GitHub as a distributed result cache:

**How it works:**
1. Before scanning, checks if company data exists in GitHub repo
2. If found, loads instantly (no API calls)
3. If not found, performs fresh scan and pushes results to GitHub
4. Results stored in `/results/{company_number}/latest.json` with timestamped archives

**Storage structure:**
```
results/
├── 00081701/
│   ├── latest.json              # Current scan results
│   ├── 20250119_143022.json     # Historical archives
│   └── 20250118_091245.json
└── 00146575/
    └── latest.json
```

**API Endpoints:**
- `GET /api/github/available-companies` - List all cached companies
- `GET /api/github/company/<number>` - Get specific company data
- Automatic push after successful scans

**UI Integration:**
- Toggle "Check GitHub Cache First" on scan form (checked by default)
- Visual indicator when data loaded from cache
- Force refresh by unchecking cache option

## 📁 Project Structure

```
signalwatch/
├── app.py                      # Flask web application
├── cli.py                      # Command-line interface
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
│
├── core/                      # Core functionality
│   ├── __init__.py
│   ├── api_client.py         # Companies House API wrapper
│   ├── pdf_processor.py      # PDF download & text extraction
│   ├── mismatch_detector.py  # Name/date comparison logic
│   ├── network_scanner.py    # Director network expansion
│   ├── batch_processor.py    # Scalable processing engine
│   └── rate_limiter.py       # Rate limit management
│
├── parsers/                   # Data parsing modules
│   ├── __init__.py
│   ├── name_parser.py        # Extract company names
│   ├── date_parser.py        # Extract dates
│   └── document_parser.py    # PDF document analysis
│
├── exporters/                 # Export functionality
│   ├── __init__.py
│   ├── csv_exporter.py       # CSV generation
│   ├── json_exporter.py      # JSON generation
│   └── html_exporter.py      # HTML report generation
│
├── templates/                 # Web interface templates
│   ├── base.html
│   ├── index.html
│   ├── results.html
│   └── report.html
│
├── static/                    # CSS, JS, images
│   ├── css/
│   │   └── astra-theme.css
│   ├── js/
│   │   └── main.js
│   └── images/
│
├── data/                      # Processing data (gitignored)
├── cache/                     # API response cache (gitignored)
├── exports/                   # Generated reports (gitignored)
│
└── tests/                     # Unit tests
    ├── __init__.py
    ├── test_api_client.py
    ├── test_mismatch_detector.py
    └── test_network_scanner.py
```

## 🔧 Configuration

Edit `.env` file to customize:

```env
# API Keys
COMPANIES_HOUSE_API_KEY=your_key_here

# Rate Limiting (600 requests per 5 minutes default)
RATE_LIMIT_REQUESTS=600
RATE_LIMIT_PERIOD=300

# Server Configuration
FLASK_PORT=5000
FLASK_DEBUG=False

# Data Storage
DATA_DIR=./data
CACHE_DIR=./cache
EXPORTS_DIR=./exports
```

## 📊 Output Examples

### Mismatch Detection
```json
{
  "company_number": "00000006",
  "mismatches": [
    {
      "type": "name_mismatch",
      "expected": "EXAMPLE LTD",
      "found": "EXAMPLE LIMITED",
      "document": "AA000001.pdf",
      "confidence": 0.95
    }
  ]
}
```

### Director Network
```json
{
  "seed_company": "00000006",
  "network": [
    {
      "director": "John Smith",
      "companies": ["00000006", "00000007", "00000008"],
      "depth": 1
    }
  ]
}
```

## 🧪 Testing

Run tests:
```powershell
pytest tests/
```

With coverage:
```powershell
pytest --cov=core --cov=parsers tests/
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for legitimate research and compliance purposes only. Users must:
- Comply with Companies House API terms of service
- Respect rate limits and usage guidelines
- Ensure proper data handling and privacy compliance
- Use responsibly and ethically

## 🆘 Support

- Issues: [GitHub Issues](https://github.com/yourusername/signalwatch/issues)
- Documentation: [Wiki](https://github.com/yourusername/signalwatch/wiki)

## 🙏 Acknowledgments

- Companies House for providing the API
- Astra theme for design inspiration
- Open source community for excellent libraries

---

**Built with ❤️ for transparency and due diligence**

📋 legal Disclaimer 

1. All data has been pulled from official sources such as Companies House. SignalWatch does not accept any responsibility for the accuracy of records or data. We simply present what is available at the time.

2. The vulnerabilities the tool detects are severe as they can enable crime and cause other systemic issues. SignalWatch does not carry out any kind of investigation or law enforcement activities. We fulfil our obligations of reporting any reasonable suspicion of crime to the relevant authorities 

3. Any claims of criminalty must be proven in the relevant court and SignalWatch takes precautions to avoid making any defamatory remarks.

4. All data is open sourced and publicy available on official databases. We urge users to keep data protection laws in mind.



