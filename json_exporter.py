"""
JSON Exporter - Export results to JSON format
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import Config


class JSONExporter:
    """Export processing results to JSON files"""
    
    def __init__(self):
        """Initialize JSON exporter"""
        Config.ensure_directories()
    
    def export_full_results(self,
                           results: Dict[str, Any],
                           output_file: Optional[Path] = None) -> Path:
        """
        Export complete results to JSON
        
        Args:
            results: Processing results from BatchProcessor
            output_file: Output file path (auto-generated if not provided)
            
        Returns:
            Path to created JSON file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Config.EXPORTS_DIR / f'results_{timestamp}.json'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON with pretty formatting
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def export_mismatches_only(self,
                              results: Dict[str, Any],
                              output_file: Optional[Path] = None) -> Path:
        """
        Export only mismatch data to JSON
        
        Args:
            results: Processing results
            output_file: Output file path
            
        Returns:
            Path to created JSON file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Config.EXPORTS_DIR / f'mismatches_{timestamp}.json'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract only mismatch data
        mismatch_data = {
            'exported_at': datetime.now().isoformat(),
            'companies': []
        }
        
        for company_result in results.get('results', []):
            company_mismatches = {
                'company_number': company_result.get('company_number'),
                'company_name': company_result.get('company_name'),
                'mismatches': company_result.get('mismatches', {})
            }
            mismatch_data['companies'].append(company_mismatches)
        
        # Write JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mismatch_data, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def export_network(self,
                      network: Dict[str, Any],
                      output_file: Optional[Path] = None) -> Path:
        """
        Export network data to JSON
        
        Args:
            network: Network data from NetworkScanner
            output_file: Output file path
            
        Returns:
            Path to created JSON file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Config.EXPORTS_DIR / f'network_{timestamp}.json'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Add export timestamp
        export_data = {
            'exported_at': datetime.now().isoformat(),
            **network
        }
        
        # Write JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def export_for_visualization(self,
                                results: Dict[str, Any],
                                output_file: Optional[Path] = None) -> Path:
        """
        Export data in format optimized for visualization
        
        Args:
            results: Processing results
            output_file: Output file path
            
        Returns:
            Path to created JSON file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Config.EXPORTS_DIR / f'viz_{timestamp}.json'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Format for visualization (nodes and edges)
        viz_data = {
            'exported_at': datetime.now().isoformat(),
            'nodes': [],
            'edges': [],
            'mismatches': []
        }
        
        # Add company nodes
        for company_result in results.get('results', []):
            node = {
                'id': company_result.get('company_number'),
                'label': company_result.get('company_name'),
                'type': 'company',
                'status': company_result.get('company_status'),
                'has_mismatches': len(company_result.get('mismatches', {}).get('mismatches', [])) > 0
            }
            viz_data['nodes'].append(node)
            
            # Add mismatch summary
            if node['has_mismatches']:
                viz_data['mismatches'].append({
                    'company_id': node['id'],
                    'company_name': node['label'],
                    'count': len(company_result.get('mismatches', {}).get('mismatches', []))
                })
        
        # Add network edges if available
        network = results.get('network')
        if network:
            # Add director nodes
            for director_id, director_data in network.get('directors', {}).items():
                node = {
                    'id': director_id,
                    'label': director_data['name'],
                    'type': 'director',
                    'company_count': director_data['company_count']
                }
                viz_data['nodes'].append(node)
            
            # Add edges
            for connection in network.get('connections', []):
                edge = {
                    'source': connection['company_number'],
                    'target': connection['director_id'],
                    'label': connection['role']
                }
                viz_data['edges'].append(edge)
        
        # Write JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(viz_data, f, indent=2, ensure_ascii=False)
        
        return output_file
