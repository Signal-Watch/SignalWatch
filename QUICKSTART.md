# Quick Start Guide

## Installation

1. **Install Python 3.9+**
   - Download from https://www.python.org/downloads/

2. **Install Tesseract OCR** (Required for PDF text extraction)
   
   **Windows:**
   ```powershell
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   # Or use Chocolatey:
   choco install tesseract
   ```

3. **Clone and Setup**
   ```powershell
   cd d:\signalwatch
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Configure API Key**
   ```powershell
   copy .env.example .env
   notepad .env  # Add your Companies House API key
   ```

## Quick Commands

### Web Interface
```powershell
python app.py
# Open http://localhost:5000 in browser
```

### Command Line

**Scan a company:**
```powershell
python cli.py scan --company 00000006
```

**Scan with network analysis:**
```powershell
python cli.py scan --companies 00000006,00000007 --expand-network --max-depth 2
```

**Search for companies:**
```powershell
python cli.py search "ACME LIMITED"
```

**Export results:**
```powershell
python cli.py export --results ./data/latest_results.json --format html
```

## Getting Your API Key

1. Visit https://developer.company-information.service.gov.uk/
2. Create an account
3. Register an application
4. Copy your API key
5. Add to `.env` file:
   ```
   COMPANIES_HOUSE_API_KEY=your_key_here
   ```

## Common Issues

### "Tesseract not found"
- Install Tesseract OCR (see installation steps above)
- Add to PATH: `C:\Program Files\Tesseract-OCR`

### "API key not found"
- Make sure `.env` file exists in the project root
- Check that `COMPANIES_HOUSE_API_KEY` is set

### Rate limit errors
- Default limit: 600 requests per 5 minutes
- Use your own API key for personal limits
- Tool automatically handles rate limiting

## Example Workflow

1. **Start web interface:**
   ```powershell
   python app.py
   ```

2. **Enter company numbers** (e.g., 00000006, 00000007)

3. **Enable network scanning** if you want to find connected companies

4. **Click "Start Analysis"**

5. **View results** showing:
   - Name mismatches
   - Date inconsistencies
   - Director connections

6. **Export reports** in CSV, JSON, or HTML format

## Support

- Documentation: See README.md
- Issues: https://github.com/yourusername/signalwatch/issues
- API Docs: https://developer.company-information.service.gov.uk/api/docs/
