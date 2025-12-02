"""
SignalWatch Web Application
Flask-based web interface for Companies House analysis
"""
from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
from pathlib import Path
import json
from datetime import datetime
import zipfile
import os
from config import Config
from core.api_client import CompaniesHouseClient
from core.batch_processor import BatchProcessor
from core.github_storage import GitHubStorage
from exporters import CSVExporter, JSONExporter, HTMLExporter
from cleanup import cleanup_exports, cleanup_cache, cleanup_data_pdfs

app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY

# Enable CORS for cross-domain requests (when frontend is on different domain)
CORS(app, origins=['*'])  # In production, replace '*' with your domain

# Ensure directories exist
Config.ensure_directories()

# Global storage for processing results (in production, use database)
processing_results = {}


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def scan_companies():
    """Start scanning companies"""
    try:
        data = request.json
        scan_mode = data.get('scan_mode', 'specific')
        company_numbers = data.get('company_numbers', [])
        scan_network = data.get('scan_network', False)
        network_depth = data.get('network_depth', 1)
        active_directors_only = data.get('active_directors_only', True)
        use_ai = data.get('use_ai', False)
        use_github_cache = data.get('use_github_cache', True)  # Check GitHub first
        ch_api_key = data.get('ch_api_key')
        xai_api_key = data.get('xai_api_key')
        oc_api_key = data.get('oc_api_key')
        
        # Validate required API keys
        if not ch_api_key:
            return jsonify({'error': 'Companies House API key is required. Please provide your own API key.'}), 400
        
        if use_ai and not xai_api_key:
            return jsonify({'error': 'XAI API key is required when AI extraction is enabled. Please provide your own API key.'}), 400
        
        # Initialize GitHub storage
        github_storage = GitHubStorage()
        
        # Handle filtered bulk scan
        if scan_mode == 'filtered':
            filters = data.get('filters', {})
            api_client = CompaniesHouseClient(ch_api_key)
            
            # Search companies with filters
            search_results = []
            alpha_start = filters.get('alpha_start', '')
            alpha_end = filters.get('alpha_end', '')
            status = filters.get('status', '')
            limit = int(filters.get('limit', 100))
            
            # Alphabetical search
            if alpha_start and alpha_end:
                start_ord = ord(alpha_start.upper())
                end_ord = ord(alpha_end.upper())
                
                for letter_ord in range(start_ord, min(end_ord + 1, start_ord + 5)):  # Max 5 letters at a time
                    letter = chr(letter_ord)
                    results = api_client.search_companies(query=letter, company_status=status or None)
                    search_results.extend(results)
                    if len(search_results) >= limit:
                        break
            else:
                results = api_client.search_companies(company_status=status or None)
                search_results = results
            
            # Apply client-side filters (CH API has limited filter support)
            
            # Filter by year if specified
            year_from = filters.get('year_from')
            year_to = filters.get('year_to')
            if year_from or year_to:
                filtered = []
                for company in search_results:
                    date_str = company.get('date_of_creation', '')
                    if date_str:
                        try:
                            year = int(date_str.split('-')[0])
                            year_from_int = int(year_from) if year_from else 0
                            year_to_int = int(year_to) if year_to else 9999
                            if year_from_int <= year <= year_to_int:
                                filtered.append(company)
                        except:
                            pass
                search_results = filtered
            
            # Filter by location if specified
            location = filters.get('location', '').strip().upper()
            if location:
                filtered = []
                for company in search_results:
                    address = company.get('address', {})
                    address_str = ' '.join([
                        address.get('locality', ''),
                        address.get('region', ''),
                        address.get('postal_code', ''),
                        address.get('address_line_1', ''),
                        address.get('country', '')
                    ]).upper()
                    if location in address_str:
                        filtered.append(company)
                search_results = filtered
            
            # Filter by SIC code if specified
            sic_codes = filters.get('sic_code', '').strip()
            if sic_codes:
                sic_list = [code.strip() for code in sic_codes.split(',')]
                filtered = []
                for company in search_results:
                    company_sics = company.get('sic_codes', [])
                    if any(sic in company_sics for sic in sic_list):
                        filtered.append(company)
                search_results = filtered
            
            # Filter by company type if specified
            company_types = filters.get('company_types', [])
            if company_types:
                filtered = []
                for company in search_results:
                    company_type = company.get('company_type', '')
                    if company_type in company_types:
                        filtered.append(company)
                search_results = filtered
            
            # Filter by dissolved date if specified (only for dissolved companies)
            dissolved_from = filters.get('dissolved_from')
            dissolved_to = filters.get('dissolved_to')
            if dissolved_from or dissolved_to:
                filtered = []
                for company in search_results:
                    date_str = company.get('date_of_cessation', '')
                    if date_str:
                        try:
                            from datetime import datetime as dt
                            dissolved_date = dt.strptime(date_str, '%Y-%m-%d').date()
                            dissolved_from_date = dt.strptime(dissolved_from, '%Y-%m-%d').date() if dissolved_from else dt(1850, 1, 1).date()
                            dissolved_to_date = dt.strptime(dissolved_to, '%Y-%m-%d').date() if dissolved_to else dt(2999, 12, 31).date()
                            if dissolved_from_date <= dissolved_date <= dissolved_to_date:
                                filtered.append(company)
                        except:
                            pass
                search_results = filtered
            
            # Extract company numbers
            company_numbers = [c.get('company_number') for c in search_results[:limit] if c.get('company_number')]
        else:
            # Format company numbers with leading zeros for specific scan
            company_numbers = [num.zfill(8) for num in company_numbers]
        
        if not company_numbers:
            return jsonify({'error': 'No company numbers provided'}), 400
        
        # Check GitHub cache first (if enabled and single company scan)
        if use_github_cache and len(company_numbers) == 1:
            company_number = company_numbers[0]
            
            # Determine folder based on settings
            folder_suffix = "Only Active Directors" if active_directors_only else "Directors"
            print(f"🔍 Checking GitHub cache: {company_number}/{folder_suffix}")
            
            # Check if this exact configuration exists
            if github_storage.check_company_exists(company_number, folder_suffix):
                cached_data = github_storage.get_company_data(company_number, folder_suffix)
                if cached_data:
                    print(f"✅ Found cached data on GitHub!")
                    
                    # Wrap single result in results array if needed
                    if 'results' not in cached_data:
                        cached_data = {'results': [cached_data]}
                    
                    # Store in session
                    result_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                    processing_results[result_id] = cached_data
                    session['last_result_id'] = result_id
                    
                    # Get summary
                    summary = {
                        'total_companies': len(cached_data.get('results', [])),
                        'total_mismatches': sum(len(r.get('mismatches', {}).get('mismatches', [])) for r in cached_data.get('results', [])),
                        'from_cache': True,
                        'cached_at': cached_data.get('_metadata', {}).get('scanned_at', 'Unknown')
                    }
                    
                    return jsonify({
                        'success': True,
                        'result_id': result_id,
                        'summary': summary,
                        'from_github_cache': True,
                        'company_number': company_number,
                        'folder_type': folder_suffix
                    })
        
        # Not in cache or cache disabled - perform fresh scan
        print(f"Performing fresh scan for {len(company_numbers)} companies")
        
        # Create API client with user's key (required)
        api_client = CompaniesHouseClient(ch_api_key)
        
        # Create batch processor
        processor = BatchProcessor(api_client)
        
        # Process companies
        results = processor.process_companies(
            company_numbers=company_numbers,
            scan_network=scan_network,
            network_depth=network_depth,
            active_only=active_directors_only,
            use_ai=use_ai
        )
        
        # Store results locally FIRST
        result_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        processing_results[result_id] = results
        session['last_result_id'] = result_id
        
        # Auto-generate CSV exports BEFORE pushing to GitHub
        if len(company_numbers) == 1:
            try:
                from exporters.csv_exporter import CSVExporter
                csv_exporter = CSVExporter()
                
                # Export mismatches CSV
                csv_exporter.export_mismatches(results, Config.EXPORTS_DIR / f'mismatches_{company_numbers[0]}_{result_id}.csv')
                print(f"✅ Generated mismatches CSV")
                
                # Export network CSV if network scan was done
                if scan_network:
                    network_csv_path = Config.EXPORTS_DIR / f'network_{company_numbers[0]}_{result_id}.csv'
                    
                    # Network data is at top level of results, not inside results array
                    network_data = results.get('network', {})
                    
                    print(f"🔍 Debug - Has network key: {bool(network_data)}")
                    print(f"🔍 Debug - Network companies: {len(network_data.get('companies', []))}")
                    print(f"🔍 Debug - Network connections: {len(network_data.get('connections', []))}")
                    
                    if network_data and network_data.get('connections'):
                        csv_exporter.export_network(network_data, network_csv_path)
                        print(f"✅ Generated network CSV: {network_csv_path.name}")
                    else:
                        print(f"⚠️ No network connections found")
                else:
                    print(f"⚠️ Network scan disabled, skipping network CSV")
                
                print(f"📊 CSV export complete")
            except Exception as e:
                print(f"Warning: Could not generate CSV exports: {e}")
        
        # Push results to GitHub (single company only)
        if len(company_numbers) == 1 and results.get('results'):
            try:
                import os
                from pathlib import Path
                
                company_number = company_numbers[0]
                company_result = results['results'][0] if results['results'] else None
                
                if company_result:
                    print(f"📤 Pushing to GitHub for {company_number} in '{folder_suffix}' folder...")
                    
                    # Add folder type to metadata
                    company_result['_folder_type'] = folder_suffix
                    
                    # Push JSON
                    push_success = github_storage.push_company_data(company_number, company_result)
                    
                    if push_success:
                        print(f"✅ JSON pushed to GitHub")
                        
                        # Push PDFs
                        pdf_dir = Path(f"./data/{company_number}")
                        if pdf_dir.exists():
                            pdf_count = 0
                            for pdf_file in pdf_dir.glob("*.pdf"):
                                github_path = f"results/{company_number}/{folder_suffix}/pdfs/{pdf_file.name}"
                                if github_storage.push_file_to_github(github_path, str(pdf_file), f"Add PDF for {company_number}"):
                                    pdf_count += 1
                            if pdf_count > 0:
                                print(f"📄 Pushed {pdf_count} PDFs")
                        
                        # Push CSV exports
                        export_dir = Path("./exports")
                        if export_dir.exists():
                            csv_count = 0
                            zip_count = 0
                            
                            # Find all CSV files for this company and result_id
                            csv_files = list(export_dir.glob(f"*{company_number}*{result_id}*.csv"))
                            print(f"🔍 Found {len(csv_files)} CSV files to push: {[f.name for f in csv_files]}")
                            print(f"🔍 Pattern used: *{company_number}*{result_id}*.csv")
                            
                            # Push all CSV files
                            for csv_file in csv_files:
                                github_path = f"results/{company_number}/{folder_suffix}/exports/{csv_file.name}"
                                print(f"📤 Pushing: {csv_file.name}")
                                if github_storage.push_file_to_github(github_path, str(csv_file), f"Add CSV for {company_number}"):
                                    csv_count += 1
                                    print(f"✅ Pushed CSV: {csv_file.name}")
                                else:
                                    print(f"❌ Failed to push: {csv_file.name}")
                            
                            # Push ZIP files
                            for zip_file in export_dir.glob(f"*{result_id}*.zip"):
                                github_path = f"results/{company_number}/{folder_suffix}/exports/{zip_file.name}"
                                if github_storage.push_file_to_github(github_path, str(zip_file), f"Add ZIP for {company_number}"):
                                    zip_count += 1
                                    print(f"📦 Pushed ZIP: {zip_file.name}")
                            
                            if csv_count > 0:
                                print(f"✅ Total: {csv_count} CSV files pushed")
                            if zip_count > 0:
                                print(f"✅ Total: {zip_count} ZIP files pushed")
                    else:
                        print(f"❌ Failed to push to GitHub")
                        
            except Exception as e:
                print(f"Warning: Could not push to GitHub: {e}")
                import traceback
                traceback.print_exc()
        
        # Cleanup old files to save disk space (important for Render 512MB limit)
        # ⚠️ Cache files are NOT cleaned - they're essential for GitHub checking
        try:
            print("🧹 Running cleanup to free disk space...")
            cleanup_exports(max_age_hours=1)    # Remove exports older than 1 hour
            cleanup_data_pdfs(max_age_days=1)   # Remove PDFs older than 1 day
            print("ℹ️  Cache files preserved - required for GitHub API checking")
        except Exception as cleanup_error:
            print(f"Warning: Cleanup failed: {cleanup_error}")
        
        # Get summary
        summary = processor.get_processing_summary(results)
        
        # Add company info for GitHub redirect
        response_data = {
            'success': True,
            'result_id': result_id,
            'summary': summary
        }
        
        # Add GitHub info for single company scans
        if len(company_numbers) == 1:
            response_data['company_number'] = company_numbers[0]
            response_data['folder_type'] = folder_suffix
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/results/<result_id>')
def get_results(result_id):
    """Get processing results"""
    # First check memory
    if result_id in processing_results:
        return jsonify(processing_results[result_id])
    
    # If not in memory, try to fetch from GitHub cache
    try:
        # Extract company number from result_id (format: YYYYMMDD_HHMMSS)
        # This is a fallback - ideally we'd store company number with result_id
        return jsonify({
            'error': 'Results expired from memory. Please check GitHub repository for stored results.',
            'github_url': 'https://github.com/Signal-Watch/signal-watch/tree/main/results'
        }), 404
    except Exception as e:
        return jsonify({'error': f'Results not found: {str(e)}'}), 404


@app.route('/api/download-pdfs/<result_id>')
def download_pdfs(result_id):
    """Download all PDFs as ZIP"""
    if result_id not in processing_results:
        return jsonify({'error': 'Results not found'}), 404
    
    results = processing_results[result_id]
    
    try:
        # Create ZIP file with all PDFs
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_path = Config.EXPORTS_DIR / f'pdfs_{timestamp}.zip'
        
        pdf_count = 0
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add PDFs from company-specific folders only for this result
            for company_result in results.get('results', []):
                company_number = company_result.get('company_number')
                company_dir = Config.DATA_DIR / company_number
                
                if company_dir.exists():
                    # Add all PDFs from this company's folder
                    for pdf_file in company_dir.glob('*.pdf'):
                        # Add with company number prefix for clarity
                        arcname = f"{company_number}/{pdf_file.name}"
                        zipf.write(pdf_file, arcname)
                        pdf_count += 1
        
        if pdf_count == 0:
            os.remove(zip_path)
            return jsonify({'error': 'No PDFs found'}), 404
        
        return send_file(zip_path, as_attachment=True, download_name=f'signalwatch_pdfs_{timestamp}.zip')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/<result_id>/<format>')
def export_results(result_id, format):
    """Export results in specified format"""
    if result_id not in processing_results:
        return jsonify({'error': 'Results not found'}), 404
    
    results = processing_results[result_id]
    
    try:
        if format == 'csv':
            exporter = CSVExporter()
            # Export mismatches
            file_path = exporter.export_mismatches(results)
            
            # If network data exists, create a ZIP with both CSVs
            if results.get('network') and results['network'].get('connections'):
                network_file_path = exporter.export_network(results['network'])
                
                # Create ZIP file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                zip_path = Config.EXPORTS_DIR / f'export_{timestamp}.zip'
                
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    zipf.write(file_path, os.path.basename(file_path))
                    zipf.write(network_file_path, os.path.basename(network_file_path))
                
                # Clean up individual files
                os.remove(file_path)
                os.remove(network_file_path)
                
                return send_file(zip_path, as_attachment=True, download_name=f'signalwatch_export_{timestamp}.zip')
            
        elif format == 'json':
            exporter = JSONExporter()
            file_path = exporter.export_full_results(results)
        elif format == 'html':
            exporter = HTMLExporter()
            file_path = exporter.export_report(results)
        else:
            return jsonify({'error': 'Invalid format'}), 400
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rate-limit')
def rate_limit_status():
    """Get rate limit status"""
    try:
        client = CompaniesHouseClient()
        status = client.get_rate_limit_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/available-companies')
def github_available_companies():
    """Get list of companies available in GitHub cache"""
    try:
        github_storage = GitHubStorage()
        companies = github_storage.list_available_companies()
        return jsonify({
            'success': True,
            'total': len(companies),
            'companies': companies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/company/<company_number>')
def github_get_company(company_number):
    """Get company data from GitHub cache"""
    try:
        github_storage = GitHubStorage()
        data = github_storage.get_company_data(company_number)
        
        if data:
            return jsonify({
                'success': True,
                'data': data
            })
        else:
            return jsonify({'error': 'Company not found in GitHub cache'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search-company')
def search_company():
    """Search for companies"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        client = CompaniesHouseClient()
        results = client.get_company_search(query)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results')
def results_page():
    """Results display page"""
    result_id = request.args.get('id') or session.get('last_result_id')
    
    if not result_id or result_id not in processing_results:
        return render_template('error.html', message='Results not found')
    
    return render_template('results.html', result_id=result_id)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='Internal server error'), 500


if __name__ == '__main__':
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
