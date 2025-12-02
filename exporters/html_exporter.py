"""
HTML Exporter - Generate HTML reports
"""
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from config import Config


class HTMLExporter:
    """Export processing results to HTML reports"""
    
    def __init__(self):
        """Initialize HTML exporter"""
        Config.ensure_directories()
    
    def export_report(self,
                     results: Dict[str, Any],
                     output_file: Optional[Path] = None,
                     include_network: bool = True) -> Path:
        """
        Generate comprehensive HTML report
        
        Args:
            results: Processing results from BatchProcessor
            output_file: Output file path (auto-generated if not provided)
            include_network: Whether to include network visualization
            
        Returns:
            Path to created HTML file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Config.EXPORTS_DIR / f'report_{timestamp}.html'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate HTML
        html = self._generate_full_report_html(results, include_network)
        
        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file
    
    def export_embeddable_widget(self,
                                results: Dict[str, Any],
                                output_file: Optional[Path] = None) -> Path:
        """
        Generate embeddable HTML widget for Astra site
        
        Args:
            results: Processing results
            output_file: Output file path
            
        Returns:
            Path to created HTML file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Config.EXPORTS_DIR / f'widget_{timestamp}.html'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate embeddable widget
        html = self._generate_widget_html(results)
        
        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file
    
    def _generate_full_report_html(self, 
                                  results: Dict[str, Any],
                                  include_network: bool) -> str:
        """Generate full HTML report"""
        
        # Calculate statistics
        total_companies = len(results.get('results', []))
        companies_with_mismatches = sum(
            1 for r in results.get('results', [])
            if len(r.get('mismatches', {}).get('mismatches', [])) > 0
        )
        total_mismatches = sum(
            len(r.get('mismatches', {}).get('mismatches', []))
            for r in results.get('results', [])
        )
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SignalWatch Report - Companies House Analysis</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            font-size: 1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .company-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fafafa;
        }}
        
        .company-card.has-mismatch {{
            border-left: 5px solid #e74c3c;
        }}
        
        .company-card.clean {{
            border-left: 5px solid #2ecc71;
        }}
        
        .company-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .company-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        
        .company-number {{
            color: #666;
            font-family: monospace;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .badge.high {{
            background: #e74c3c;
            color: white;
        }}
        
        .badge.medium {{
            background: #f39c12;
            color: white;
        }}
        
        .badge.low {{
            background: #3498db;
            color: white;
        }}
        
        .badge.success {{
            background: #2ecc71;
            color: white;
        }}
        
        .mismatch-list {{
            margin-top: 15px;
        }}
        
        .mismatch-item {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 3px solid #f39c12;
        }}
        
        .mismatch-type {{
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 5px;
        }}
        
        .mismatch-detail {{
            color: #666;
            font-size: 0.9em;
            margin: 5px 0;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 50px;
        }}
        
        .timestamp {{
            color: #999;
            font-size: 0.9em;
        }}
        
        @media print {{
            .container {{
                max-width: 100%;
            }}
            .stat-card {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SignalWatch Report</h1>
            <div class="subtitle">Companies House Data Analysis</div>
            <div class="timestamp">Generated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="number">{total_companies}</div>
                <div class="label">Companies Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="number">{companies_with_mismatches}</div>
                <div class="label">With Mismatches</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_mismatches}</div>
                <div class="label">Total Issues Found</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_companies - companies_with_mismatches}</div>
                <div class="label">Clean Records</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Analysis Results</h2>
            {self._generate_company_cards(results)}
        </div>
        
        {self._generate_network_section(results) if include_network and results.get('network') else ''}
        
        <div class="footer">
            <p>Report generated by <strong>SignalWatch</strong></p>
            <p>Data sourced from Companies House</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_company_cards(self, results: Dict[str, Any]) -> str:
        """Generate HTML for company cards"""
        cards = []
        
        for company_result in results.get('results', []):
            company_number = company_result.get('company_number', 'Unknown')
            company_name = company_result.get('company_name', 'Unknown')
            mismatch_data = company_result.get('mismatches', {})
            mismatches = mismatch_data.get('mismatches', [])
            
            has_mismatches = len(mismatches) > 0
            card_class = 'has-mismatch' if has_mismatches else 'clean'
            
            # Build mismatch list
            mismatch_html = ''
            if mismatches:
                mismatch_items = []
                for mismatch in mismatches:
                    severity = mismatch.get('severity', 'low')
                    mtype = mismatch.get('type', 'unknown').replace('_', ' ').title()
                    document = mismatch.get('document', 'N/A')
                    
                    details = []
                    if 'expected_names' in mismatch:
                        details.append(f"Expected: {', '.join(mismatch['expected_names'][:2])}")
                        details.append(f"Found: {mismatch['found_name']}")
                    if 'expected_date' in mismatch:
                        details.append(f"Expected: {mismatch['expected_date']}")
                        details.append(f"Found: {mismatch['found_date']}")
                    if 'message' in mismatch:
                        details.append(mismatch['message'])
                    
                    detail_html = ''.join([f'<div class="mismatch-detail">{d}</div>' for d in details])
                    
                    mismatch_items.append(f'''
                        <div class="mismatch-item">
                            <div class="mismatch-type"><span class="badge {severity}">{severity}</span> {mtype}</div>
                            <div class="mismatch-detail">Document: {document}</div>
                            {detail_html}
                        </div>
                    ''')
                
                mismatch_html = f'<div class="mismatch-list">{"".join(mismatch_items)}</div>'
            else:
                mismatch_html = '<div style="color: #2ecc71; font-weight: bold; margin-top: 10px;">✓ No mismatches detected</div>'
            
            card = f'''
                <div class="company-card {card_class}">
                    <div class="company-header">
                        <div>
                            <div class="company-name">{company_name}</div>
                            <div class="company-number">{company_number}</div>
                        </div>
                        <div>
                            {'<span class="badge success">Clean</span>' if not has_mismatches else f'<span class="badge high">{len(mismatches)} Issues</span>'}
                        </div>
                    </div>
                    {mismatch_html}
                </div>
            '''
            cards.append(card)
        
        return ''.join(cards)
    
    def _generate_network_section(self, results: Dict[str, Any]) -> str:
        """Generate network visualization section"""
        network = results.get('network', {})
        stats = network.get('statistics', {})
        
        return f'''
        <div class="section">
            <h2>Director Network Analysis</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">{stats.get('total_companies', 0)}</div>
                    <div class="label">Connected Companies</div>
                </div>
                <div class="stat-card">
                    <div class="number">{stats.get('total_directors', 0)}</div>
                    <div class="label">Unique Directors</div>
                </div>
                <div class="stat-card">
                    <div class="number">{stats.get('total_connections', 0)}</div>
                    <div class="label">Total Connections</div>
                </div>
                <div class="stat-card">
                    <div class="number">{stats.get('depth_reached', 0)}</div>
                    <div class="label">Network Depth</div>
                </div>
            </div>
            <p style="color: #666; margin-top: 20px;">
                Network analysis reveals connections between companies through shared directors.
                Detailed connection data is available in the JSON/CSV exports.
            </p>
        </div>
        '''
    
    def _generate_widget_html(self, results: Dict[str, Any]) -> str:
        """Generate embeddable widget HTML"""
        
        # Simplified version for embedding
        html = f"""
<div id="signalwatch-widget" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    <style>
        #signalwatch-widget * {{
            box-sizing: border-box;
        }}
        #signalwatch-widget .sw-title {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        #signalwatch-widget .sw-stat {{
            display: inline-block;
            margin-right: 20px;
            padding: 10px 15px;
            background: #f0f0f0;
            border-radius: 5px;
        }}
        #signalwatch-widget .sw-stat-number {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}
        #signalwatch-widget .sw-stat-label {{
            font-size: 0.9em;
            color: #666;
        }}
    </style>
    
    <div class="sw-title">Companies House Analysis Summary</div>
    
    <div style="margin-bottom: 20px;">
        <div class="sw-stat">
            <div class="sw-stat-number">{len(results.get('results', []))}</div>
            <div class="sw-stat-label">Companies</div>
        </div>
        <div class="sw-stat">
            <div class="sw-stat-number">{sum(1 for r in results.get('results', []) if len(r.get('mismatches', {}).get('mismatches', [])) > 0)}</div>
            <div class="sw-stat-label">With Issues</div>
        </div>
        <div class="sw-stat">
            <div class="sw-stat-number">{sum(len(r.get('mismatches', {}).get('mismatches', [])) for r in results.get('results', []))}</div>
            <div class="sw-stat-label">Total Issues</div>
        </div>
    </div>
    
    <div style="font-size: 0.9em; color: #666;">
        <p>Last updated: {datetime.now().strftime('%d %B %Y')}</p>
    </div>
</div>
"""
        return html
