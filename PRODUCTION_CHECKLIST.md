# Production Deployment Checklist

## ✅ Completed Changes

### 1. Frontend Validation (templates/index.html)
- ✅ Companies House API key marked as **Required** with red asterisk
- ✅ HTML5 `required` attribute added - browser blocks submission if empty
- ✅ Warning text: "⚠️ Required - You must provide your own API key"
- ✅ XAI API key conditional requirement: "⚠️ Required if 'Use AI Extraction' is enabled"
- ✅ Help links with `target="_blank"` for user guidance

### 2. Backend Validation (app.py)
- ✅ Added validation at `/api/scan` endpoint (lines 52-56)
- ✅ Returns 400 error if `ch_api_key` is missing
- ✅ Returns 400 error if `use_ai=True` and `xai_api_key` is missing
- ✅ Removed fallback to Config defaults in API client initialization
- ✅ Clear error messages for missing keys

### 3. Documentation (README.md)
- ✅ Updated Companies House API key section to emphasize **REQUIRED**
- ✅ Updated AI API key section to emphasize conditional requirement
- ✅ Added warning symbols and clear instructions

## 🚀 Pre-Deployment Steps

### 1. Clean Environment Variables
**Action Required:** Remove or clear default API keys from `.env` file

**Current State:**
```dotenv
COMPANIES_HOUSE_API_KEY=your_key
XAI_API_KEY=xai_your_key
```

**Production State:**
```dotenv
# Companies House API Key - Users provide their own via web interface
COMPANIES_HOUSE_API_KEY=

# AI API Keys - Users provide their own when enabling AI extraction
XAI_API_KEY=
OPENAI_API_KEY=

# GitHub Token - Keep for caching functionality
GITHUB_TOKEN=your_key
```

### 2. Test Validation Flow
1. **Start the application:**
   ```powershell
   python app.py
   ```

2. **Test required CH API key:**
   - Try submitting scan without CH API key → Should get browser validation error
   - Try submitting with empty string via API → Should get 400 error
   - Try submitting with valid key → Should work

3. **Test conditional AI key:**
   - Enable "Use AI Extraction" toggle without XAI key → Should get 400 error
   - Disable AI extraction, no XAI key → Should work
   - Enable AI extraction with valid XAI key → Should work

4. **Test GitHub caching:**
   - Scan a company number that's already in GitHub cache
   - Should return cached result with GitHub redirect button

### 3. Security Review
- ✅ No default API keys in production code
- ✅ GitHub token remains for caching (authorized repo access)
- ✅ Validation prevents unauthorized API usage
- ✅ Error messages don't expose sensitive information

### 4. User Experience
- ✅ Clear error messages guide users to provide their own keys
- ✅ Help links provided for obtaining API keys
- ✅ Conditional requirements clearly stated
- ✅ GitHub redirect works for cached results

## 📦 Deployment Workflow

### Option A: Manual Deployment
1. Clear API keys from `.env`
2. Test locally with user-provided keys
3. Deploy to hosting service (Heroku, Railway, etc.)
4. Set environment variables in hosting dashboard:
   - `GITHUB_TOKEN` (for caching)
   - `FLASK_SECRET_KEY` (generate new random string)
   - Leave `COMPANIES_HOUSE_API_KEY` and `XAI_API_KEY` empty

### Option B: Docker Deployment
1. Build Docker image without API keys in `.env`
2. Mount GitHub token as secret
3. Deploy to container hosting (Docker Hub, AWS ECS, etc.)

## 🔍 Post-Deployment Verification

### Test Cases
1. **New user flow:**
   - User visits site for first time
   - User clicks API key help links
   - User enters their own Companies House key
   - User performs scan → Success

2. **AI extraction flow:**
   - User enables "Use AI Extraction"
   - User attempts scan without XAI key → Gets clear error
   - User enters their own XAI key
   - User performs scan → Success

3. **GitHub cache flow:**
   - User scans company that was scanned before
   - Results load from GitHub cache (instant)
   - "View on GitHub" button redirects to repository folder

4. **Error handling:**
   - Invalid API key → Clear error from Companies House API
   - Rate limit exceeded → Retry logic kicks in
   - Network error → User-friendly error message

## 📊 Monitoring

### Key Metrics to Track
- **User-provided API key rate:** How many scans use user keys vs fail validation
- **GitHub cache hit rate:** % of scans served from cache
- **API error rate:** Track 400 validation errors vs 500 server errors
- **Scan completion rate:** % of scans that complete successfully

### Log Analysis
Monitor logs for:
- `"Companies House API key is required"` → Frontend validation bypassed
- `"XAI API key is required when AI extraction is enabled"` → Conditional validation working
- `"✅ Found cached result in GitHub"` → Cache efficiency
- `"Performing fresh scan"` → New API calls

## 🐛 Rollback Plan

If issues occur:
1. **Immediate:** Re-enable default API keys in `.env` temporarily
2. **Remove:** Required attribute from HTML form
3. **Disable:** Backend validation (comment out lines 52-56 in `app.py`)
4. **Notify:** Users via site banner that keys are temporarily shared
5. **Fix:** Address specific issue and re-deploy

## ✨ Success Criteria

- ✅ No default API keys in production environment
- ✅ All users provide their own Companies House API key
- ✅ AI extraction only works with user-provided AI API key
- ✅ Clear error messages guide users
- ✅ GitHub caching reduces overall API usage
- ✅ No security vulnerabilities introduced
- ✅ User experience remains smooth and intuitive

## 📝 Notes

- **GitHub Token:** Kept in `.env` for caching - this is admin-level, not user-provided
- **Rate Limiting:** Still applies per API key (600 req / 5 min per key)
- **Cost Optimization:** User-provided keys prevent token exhaustion
- **Scalability:** Each user's API quota is independent
