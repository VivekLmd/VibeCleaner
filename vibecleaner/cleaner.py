"""Core downloads folder cleaner and organizer."""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import json

class DownloadsCleaner:
    """Smart downloads folder organizer and cleaner."""
    
    DEFAULT_RULES = {
        'Documents': {
            'extensions': ['.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf', '.tex', '.wpd'],
            'folder': 'Documents'
        },
        'Images': {
            'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp', '.tiff'],
            'folder': 'Images'
        },
        'Videos': {
            'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg'],
            'folder': 'Videos'
        },
        'Audio': {
            'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'],
            'folder': 'Audio'
        },
        'Archives': {
            'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
            'folder': 'Archives'
        },
        'Code': {
            'extensions': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c', '.rs', '.go', '.php'],
            'folder': 'Code'
        },
        'Data': {
            'extensions': ['.json', '.xml', '.csv', '.sql', '.db', '.sqlite'],
            'folder': 'Data'
        },
        'Executables': {
            'extensions': ['.exe', '.msi', '.app', '.deb', '.rpm', '.dmg', '.pkg'],
            'folder': 'Software'
        }
    }
    
    def __init__(self, downloads_path: Optional[Path] = None, dry_run: bool = True):
        """Initialize the cleaner with target directory and options."""
        if downloads_path:
            self.downloads_path = Path(downloads_path)
        else:
            self.downloads_path = Path.home() / 'Downloads'
        
        self.dry_run = dry_run
        self.operation_log = []
        self.stats = {
            'files_moved': 0,
            'files_deleted': 0,
            'duplicates_removed': 0,
            'space_freed': 0
        }
        
    def organize_files(self, custom_rules: Optional[Dict] = None) -> Dict[str, List[str]]:
        """Organize files by type into categorized folders."""
        rules = custom_rules or self.DEFAULT_RULES
        organized = {}
        
        if not self.downloads_path.exists():
            raise FileNotFoundError(f"Downloads folder not found: {self.downloads_path}")
        
        for file_path in self.downloads_path.iterdir():
            if file_path.is_file():
                category = self._categorize_file(file_path, rules)
                if category:
                    dest_folder = self.downloads_path / rules[category]['folder']
                    
                    if not self.dry_run:
                        dest_folder.mkdir(exist_ok=True)
                        dest_file = dest_folder / file_path.name
                        
                        # Handle duplicates with numbering
                        if dest_file.exists():
                            dest_file = self._get_unique_filename(dest_file)
                        
                        shutil.move(str(file_path), str(dest_file))
                        self.stats['files_moved'] += 1
                        
                    organized.setdefault(category, []).append(file_path.name)
                    self._log_operation('move', file_path, dest_folder)
        
        return organized
    
    def remove_old_files(self, days: int = 30, min_size_mb: float = 0) -> List[Path]:
        """Remove or archive files older than specified days."""
        old_files = []
        cutoff_date = datetime.now() - timedelta(days=days)
        min_size_bytes = min_size_mb * 1024 * 1024
        
        for file_path in self.downloads_path.rglob('*'):
            if file_path.is_file():
                file_stat = file_path.stat()
                file_modified = datetime.fromtimestamp(file_stat.st_mtime)
                
                if file_modified < cutoff_date and file_stat.st_size >= min_size_bytes:
                    old_files.append(file_path)
                    
                    if not self.dry_run:
                        # Move to trash or archive folder
                        archive_path = self.downloads_path / 'Archive' / file_path.relative_to(self.downloads_path)
                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(archive_path))
                        self.stats['files_moved'] += 1
                        self.stats['space_freed'] += file_stat.st_size
                    
                    self._log_operation('archive', file_path, None)
        
        return old_files
    
    def find_duplicates(self) -> Dict[str, List[Path]]:
        """Find duplicate files based on content hash."""
        hash_map = {}
        duplicates = {}
        
        for file_path in self.downloads_path.rglob('*'):
            if file_path.is_file():
                file_hash = self._hash_file(file_path)
                if file_hash in hash_map:
                    duplicates.setdefault(file_hash, [hash_map[file_hash]])
                    duplicates[file_hash].append(file_path)
                else:
                    hash_map[file_hash] = file_path
        
        return duplicates
    
    def remove_duplicates(self, keep_newest: bool = True) -> int:
        """Remove duplicate files, keeping either newest or oldest."""
        duplicates = self.find_duplicates()
        removed_count = 0
        
        for file_hash, file_list in duplicates.items():
            if len(file_list) > 1:
                # Sort by modification time
                file_list.sort(key=lambda p: p.stat().st_mtime, reverse=keep_newest)
                
                # Keep first, remove rest
                for file_path in file_list[1:]:
                    if not self.dry_run:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        self.stats['duplicates_removed'] += 1
                        self.stats['space_freed'] += file_size
                    
                    removed_count += 1
                    self._log_operation('delete_duplicate', file_path, None)
        
        return removed_count
    
    def clean(self, organize: bool = True, remove_old: bool = False, 
              remove_duplicates: bool = False, old_days: int = 30) -> Dict:
        """Run complete cleaning operation with specified options."""
        results = {
            'organized': {},
            'old_files': [],
            'duplicates_removed': 0,
            'stats': self.stats
        }
        
        if organize:
            results['organized'] = self.organize_files()
        
        if remove_old:
            results['old_files'] = self.remove_old_files(days=old_days)
        
        if remove_duplicates:
            results['duplicates_removed'] = self.remove_duplicates()
        
        return results
    
    def _categorize_file(self, file_path: Path, rules: Dict) -> Optional[str]:
        """Determine category for a file based on extension."""
        file_ext = file_path.suffix.lower()
        
        for category, rule in rules.items():
            if file_ext in rule['extensions']:
                return category
        
        return None
    
    def _hash_file(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate MD5 hash of file content."""
        hash_md5 = hashlib.md5()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return str(file_path)  # Fallback to path if can't read
    
    def _get_unique_filename(self, file_path: Path) -> Path:
        """Generate unique filename by adding number suffix."""
        base = file_path.stem
        ext = file_path.suffix
        parent = file_path.parent
        counter = 1
        
        while True:
            new_path = parent / f"{base}_{counter}{ext}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _log_operation(self, operation: str, source: Path, destination: Optional[Path]):
        """Log file operation for undo/reporting."""
        self.operation_log.append({
            'operation': operation,
            'source': str(source),
            'destination': str(destination) if destination else None,
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run
        })
    
    def save_log(self, log_file: Path):
        """Save operation log to file."""
        with open(log_file, 'w') as f:
            json.dump(self.operation_log, f, indent=2)
    
    def get_statistics(self) -> Dict:
        """Get cleaning statistics."""
        return {
            **self.stats,
            'total_operations': len(self.operation_log),
            'space_freed_mb': round(self.stats['space_freed'] / (1024 * 1024), 2)
        }