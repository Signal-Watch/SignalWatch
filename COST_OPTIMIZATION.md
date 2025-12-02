# Cost Optimization Guide 💰

SignalWatch is designed to **minimize costs** by using free methods first, only falling back to paid AI when needed.

## Free Methods (No Cost)

### 1. **OCR with Tesseract** ✅ FREE
- **Default method** for all PDF text extraction
- Works great for most Companies House documents
- Zero cost, unlimited usage
- Install once, use forever

### 2. **Companies House API** ✅ FREE
- 600 requests per 5 minutes
- Completely free, no credit card needed
- Create account at: https://developer.company-information.service.gov.uk/

### 3. **Native PDF Text** ✅ FREE
- For PDFs with embedded text (not scanned)
- Always tried first
- Zero cost

## Paid Methods (Optional)

### XAI (Grok) - **Recommended for AI** 🌟

**Why Grok?**
- ✅ **Much cheaper** than OpenAI
- ✅ **Faster** responses (grok-beta model)
- ✅ Better for bulk processing
- ✅ Vision capabilities for scanned documents

**Setup:**
```bash
# .env file
XAI_API_KEY=xai_your_key
AI_PROVIDER=xai
XAI_MODEL=grok-beta  # Fastest, cheapest
```

**Cost:** ~$0.50 per 1M tokens (input) vs OpenAI's ~$5-$10

### OpenAI (Alternative)

```bash
# .env file
OPENAI_API_KEY=your_key_here
AI_PROVIDER=openai
```

**Cost:** ~$5-$10 per 1M tokens

## Cost Minimization Strategy

### Default Behavior (Recommended) 💚

The tool is **configured to use zero-cost methods by default**:

1. **Try native PDF text** (free)
2. **Try Tesseract OCR** (free)
3. **Only use AI if both fail** (costs tokens)

This means:
- ✅ Most documents: **$0 cost**
- ✅ Only complex/scanned docs use AI
- ✅ You control when AI is used

### Configuration

```python
# In batch_processor.py (line ~230)
parsed = self.document_parser.parse_document(
    pdf_path, 
    use_ocr=True,        # FREE - always enabled
    use_ai=False,        # PAID - disabled by default
    prefer_ocr=True      # Try free method first
)
```

**To enable AI extraction:**
```python
use_ai=True  # Only set this if OCR fails
```

### Command Line Control

```powershell
# Free mode (default) - uses only OCR
python cli.py scan --company 00000006

# AI mode - enable AI fallback for difficult documents
# (requires modifying code or adding CLI flag)
```

## Real Cost Examples

### Scenario 1: 100 Companies (Typical)
- Companies House API calls: **Free** ✅
- 100 company profiles: **Free** ✅
- 500 filing history requests: **Free** ✅
- 50 PDFs downloaded: **Free** ✅
- OCR on 50 PDFs: **Free** ✅
- **Total: $0** 💚

### Scenario 2: 100 Companies with AI Fallback
- Same as above: **Free** ✅
- 5 difficult PDFs need AI (OCR failed): **~$0.10** 💛
- Using XAI Grok: **~$0.02** 🌟
- **Total: $0.02-$0.10** 💚

### Scenario 3: Heavy AI Usage (All PDFs)
- If you force AI on all 50 PDFs:
- With OpenAI: **~$2.50** ⚠️
- With XAI Grok: **~$0.50** 💛
- **Not recommended** - OCR works fine for 90%+ of documents

## Recommendations

### For Maximum Savings 🌟

1. **Use default settings** (AI disabled)
2. **Install Tesseract OCR** properly
3. **Use your own CH API key** (free, personal rate limit)
4. **Process in batches** during off-peak hours

### When to Enable AI

Only enable AI extraction if:
- ✅ OCR consistently fails on your documents
- ✅ Documents have complex layouts
- ✅ Hand-written sections need extraction
- ✅ You need 100% accuracy

### Which AI to Choose

If you need AI:
1. **XAI (Grok)** - Best choice for cost/performance
2. **OpenAI** - Higher quality, higher cost

## Monitoring Costs

The tool tells you when it uses AI:
```
Processing document ABC123.pdf...
  ✅ Extracted with OCR (free)

Processing document XYZ789.pdf...
  💰 Using AI extraction (costs tokens) for XYZ789.pdf
```

Watch for 💰 symbol = AI is being used (costs money)

## Bottom Line

**Default configuration = $0 cost for most use cases** ✅

You only pay if:
- You manually enable AI extraction
- OCR fails and you have AI fallback enabled

**Recommended setup for minimal cost:**
```env
# .env
COMPANIES_HOUSE_API_KEY=your_free_key_here
# No AI keys = $0 cost, pure OCR mode
```

**If you need AI occasionally:**
```env
# .env
COMPANIES_HOUSE_API_KEY=your_free_key_here
XAI_API_KEY=your_xai_key_here
AI_PROVIDER=xai
XAI_MODEL=grok-beta
```

Then it uses AI only when OCR fails = minimal cost! 🎉
