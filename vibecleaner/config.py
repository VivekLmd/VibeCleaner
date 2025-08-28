"""Configuration management for VibeCleaner."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any

def get_default_config() -> Dict[str, Any]:
    """Get default configuration for VibeCleaner."""
    return {
        'downloads_path': str(Path.home() / 'Downloads'),
        'organize': {
            'Documents': {
                'extensions': ['.pdf', '.doc', '.docx', '.txt', '.odt'],
                'path': str(Path.home() / 'Documents' / 'Downloads')
            },
            'Images': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'],
                'path': str(Path.home() / 'Pictures' / 'Downloads')
            },
            'Videos': {
                'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
                'path': str(Path.home() / 'Videos' / 'Downloads')
            },
            'Archives': {
                'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz'],
                'path': str(Path.home() / 'Downloads' / 'Archives')
            }
        },
        'cleanup': {
            'delete_after_days': 90,
            'archive_after_days': 30,
            'min_file_size': '1MB',
            'remove_duplicates': True
        },
        'safety': {
            'dry_run_default': True,
            'backup_before_delete': True,
            'whitelist_patterns': [
                'important_*',
                '*.key',
                '*.license'
            ]
        }
    }

def load_config(config_path: Path = None) -> Dict[str, Any]:
    """Load configuration from file or return defaults."""
    if config_path is None:
        config_path = Path.home() / '.vibecleaner.yml'
    
    if not config_path.exists():
        return get_default_config()
    
    try:
        with open(config_path) as f:
            if config_path.suffix in ['.yml', '.yaml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)
    except Exception:
        return get_default_config()

def save_config(config: Dict[str, Any], config_path: Path = None):
    """Save configuration to file."""
    if config_path is None:
        config_path = Path.home() / '.vibecleaner.yml'
    
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        if config_path.suffix in ['.yml', '.yaml']:
            yaml.safe_dump(config, f, default_flow_style=False)
        else:
            json.dump(config, f, indent=2)