# Example Usage and Scenarios

## Scenario 1: Single Company Due Diligence

Check a specific company for filing inconsistencies:

```powershell
python cli.py scan --company 00000006 --export html
```

This will:
1. Fetch company profile and filing history
2. Download relevant PDF documents
3. Extract and parse company names and dates
4. Compare with official records
5. Generate an HTML report

## Scenario 2: Bulk Company Analysis

Analyze multiple companies at once:

```powershell
python cli.py scan --companies "00000006,00000007,00000008,00000009" --export csv
```

Results will include:
- CSV file with all detected mismatches
- Summary CSV with statistics per company
- JSON file with complete results

## Scenario 3: Director Network Discovery

Find connected companies through shared directors:

```powershell
python cli.py scan --company 00000006 --expand-network --max-depth 2
```

This discovers:
- Directors of the seed company
- Other companies where those directors serve
- Second-level connections (directors of connected companies)

Example output:
```
🕸️ Network Analysis:
   Connected companies: 23
   Unique directors: 15
   Total connections: 45
```

## Scenario 4: Using the Web Interface

1. Start the server:
```powershell
python app.py
```

2. Open browser to `http://localhost:5000`

3. Enter company numbers in the search form

4. Select options:
   - ☑ Scan director networks
   - Network Depth: 2 levels

5. Optionally add your API key for personal rate limits

6. Click "Start Analysis"

7. View results with:
   - Visual summary cards
   - Detailed mismatch listings
   - Network statistics
   - Export buttons for CSV/JSON/HTML

## Scenario 5: Resume Interrupted Scan

If a scan is interrupted (e.g., network issue, rate limit):

```powershell
python cli.py resume --checkpoint-file ./data/checkpoint_20250114_120000.json
```

The tool will:
- Load the checkpoint
- Skip already-processed companies
- Continue from where it left off
- Update the checkpoint file

## Scenario 6: Targeted Network Analysis

Focus only on network discovery without mismatch detection:

```powershell
python cli.py network --companies "00000006,00000007" --max-depth 3 --max-companies 200
```

This generates:
- Detailed network map
- Shared directors list
- Company clusters
- Connection statistics

## Scenario 7: Company Search

Find companies before scanning:

```powershell
python cli.py search "ACME TRADING"
```

Output:
```
📋 Found 15 results:
   00123456: ACME TRADING LIMITED
      Status: active
   00234567: ACME TRADING (UK) LIMITED
      Status: active
   ...
```

## Scenario 8: API Integration

Use SignalWatch as a library in your own code:

```python
from core.api_client import CompaniesHouseClient
from core.batch_processor import BatchProcessor

# Initialize
processor = BatchProcessor()

# Process companies
results = processor.process_companies(
    company_numbers=['00000006', '00000007'],
    scan_network=True,
    network_depth=2
)

# Access results
for company_result in results['results']:
    print(f"Company: {company_result['company_name']}")
    mismatches = company_result['mismatches']['mismatches']
    print(f"Issues found: {len(mismatches)}")
```

## Scenario 9: Embeddable Report Widget

Generate HTML widget for embedding in your website:

```python
from exporters import HTMLExporter

exporter = HTMLExporter()
widget_path = exporter.export_embeddable_widget(results)

# Copy the HTML from widget_path and embed in your site
```

The widget includes:
- Compact summary statistics
- Styled to match Astra theme
- Standalone CSS (no dependencies)
- Ready to embed with `<iframe>` or directly

## Scenario 10: Automated Monitoring

Set up scheduled scans for compliance monitoring:

```powershell
# Create a batch script (monitor.ps1)
$companies = "00000006,00000007,00000008"
python cli.py scan --companies $companies --export csv

# Email or save results for review
```

Schedule with Windows Task Scheduler to run daily/weekly.

## Tips

**Optimize Rate Limits:**
- Use your own API key: `--api-key YOUR_KEY`
- Process in smaller batches during off-hours
- The tool automatically respects rate limits

**Better OCR Results:**
- Ensure Tesseract is properly installed
- For critical documents, use AI extraction (requires OpenAI API key)

**Performance:**
- Network scans can discover many companies quickly
- Use `--max-companies` to limit scope
- Lower `--max-depth` for faster scans

**Export Formats:**
- **CSV**: Best for Excel/spreadsheet analysis
- **JSON**: For programmatic processing or archiving
- **HTML**: For human-readable reports and sharing
