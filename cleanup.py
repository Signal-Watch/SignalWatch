"""
Cleanup utility for temporary files
Automatically removes old exports and cached files to save disk space
"""
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from config import Config


def cleanup_exports(max_age_hours: int = 24):
    """
    Remove export files older than specified hours
    
    Args:
        max_age_hours: Maximum age of files to keep (default: 24 hours)
    """
    exports_dir = Config.EXPORTS_DIR
    if not exports_dir.exists():
        return
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    removed_count = 0
    
    for file_path in exports_dir.glob('**/*'):
        if file_path.is_file():
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_time:
                try:
                    file_path.unlink()
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
    
    print(f"✅ Cleaned up {removed_count} old export files")
    return removed_count


def cleanup_cache(max_age_days: int = 7):
    """
    ⚠️ DISABLED - Cache files are essential for GitHub checking
    
    Cache files store GitHub API responses to check if company already scanned.
    DO NOT delete these - they prevent duplicate API calls and save costs.
    """
    print("ℹ️  Cache cleanup disabled - cache files are essential for GitHub checking")
    return 0


def cleanup_data_pdfs(max_age_days: int = 3):
    """
    Remove downloaded PDFs older than specified days
    
    Args:
        max_age_days: Maximum age of PDFs (default: 3 days)
    """
    data_dir = Config.DATA_DIR
    if not data_dir.exists():
        return
    
    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    removed_count = 0
    removed_size = 0
    
    for file_path in data_dir.glob('**/*.pdf'):
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        if file_time < cutoff_time:
            try:
                file_size = file_path.stat().st_size
                file_path.unlink()
                removed_count += 1
                removed_size += file_size
            except Exception as e:
                print(f"Error removing {file_path}: {e}")
    
    size_mb = removed_size / (1024 * 1024)
    print(f"✅ Cleaned up {removed_count} PDFs ({size_mb:.2f} MB)")
    return removed_count


def cleanup_all():
    """
    Run all cleanup operations
    ⚠️ Cache files are NOT cleaned - they're essential for GitHub checking
    """
    print("🧹 Starting cleanup operations...")
    cleanup_exports(max_age_hours=24)  # Remove exports older than 24 hours
    cleanup_data_pdfs(max_age_days=3)   # Remove PDFs older than 3 days
    print("ℹ️  Cache files preserved - required for GitHub checking")
    print("✅ Cleanup complete!")


def get_disk_usage():
    """
    Get current disk usage of data directories
    """
    total_size = 0
    
    for directory in [Config.DATA_DIR, Config.CACHE_DIR, Config.EXPORTS_DIR]:
        if directory.exists():
            for file_path in directory.glob('**/*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
    
    size_mb = total_size / (1024 * 1024)
    return size_mb


if __name__ == '__main__':
    # Show current usage
    usage = get_disk_usage()
    print(f"📊 Current disk usage: {usage:.2f} MB")
    
    # Run cleanup
    cleanup_all()
    
    # Show usage after cleanup
    usage_after = get_disk_usage()
    print(f"📊 Disk usage after cleanup: {usage_after:.2f} MB")
    print(f"💾 Space freed: {usage - usage_after:.2f} MB")
