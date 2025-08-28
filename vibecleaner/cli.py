"""VibeCleaner CLI - Smart Downloads Folder Organizer."""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from . import __version__
from .cleaner import DownloadsCleaner
from .config import load_config, save_config, get_default_config
from .scheduler import setup_schedule, remove_schedule

def cmd_init(args):
    """Initialize VibeCleaner with default configuration."""
    config = get_default_config()
    config_path = Path.home() / '.vibecleaner.yml'
    
    if config_path.exists() and not args.force:
        print(f"Configuration already exists at {config_path}")
        print("Use --force to overwrite")
        return
    
    save_config(config, config_path)
    print(f"VibeCleaner {__version__} initialized!")
    print(f"Configuration saved to: {config_path}")
    print(f"Default downloads folder: {config['downloads_path']}")
    print("\nNext steps:")
    print("  1. Edit configuration: vibecleaner config")
    print("  2. Preview cleaning: vibecleaner clean --dry-run")
    print("  3. Clean downloads: vibecleaner clean")

def cmd_clean(args):
    """Clean and organize downloads folder."""
    config = load_config()
    downloads_path = Path(args.path or config.get('downloads_path', '~/Downloads')).expanduser()
    
    # Initialize cleaner
    cleaner = DownloadsCleaner(downloads_path, dry_run=args.dry_run)
    
    # Print mode
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        print("🧹 CLEANING MODE - Files will be organized")
    
    print(f"📁 Target folder: {downloads_path}\n")
    
    # Run cleaning operations
    results = cleaner.clean(
        organize=not args.no_organize,
        remove_old=args.remove_old,
        remove_duplicates=args.duplicates,
        old_days=args.older_than or config.get('cleanup', {}).get('delete_after_days', 30)
    )
    
    # Display results
    if results['organized']:
        print("📂 Files organized by type:")
        for category, files in results['organized'].items():
            print(f"  {category}: {len(files)} files")
    
    if results['old_files']:
        print(f"\n🗓️ Old files archived: {len(results['old_files'])} files")
    
    if results['duplicates_removed']:
        print(f"\n♊ Duplicates removed: {results['duplicates_removed']} files")
    
    # Show statistics
    stats = cleaner.get_statistics()
    print("\n📊 Statistics:")
    print(f"  Files moved: {stats['files_moved']}")
    print(f"  Files deleted: {stats['files_deleted']}")
    print(f"  Duplicates removed: {stats['duplicates_removed']}")
    print(f"  Space freed: {stats['space_freed_mb']} MB")
    
    # Save log
    if not args.dry_run and args.log:
        log_path = Path(args.log)
        cleaner.save_log(log_path)
        print(f"\n📝 Operation log saved to: {log_path}")

def cmd_watch(args):
    """Watch downloads folder for real-time organization."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("Error: watchdog package required for watch mode")
        print("Install with: pip install watchdog")
        return 1
    
    config = load_config()
    downloads_path = Path(args.path or config.get('downloads_path', '~/Downloads')).expanduser()
    
    class DownloadHandler(FileSystemEventHandler):
        def __init__(self):
            self.cleaner = DownloadsCleaner(downloads_path, dry_run=False)
        
        def on_created(self, event):
            if not event.is_directory:
                print(f"New file detected: {event.src_path}")
                # Small delay to ensure file is fully downloaded
                import time
                time.sleep(1)
                self.cleaner.organize_files()
                print(f"Organized: {Path(event.src_path).name}")
    
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, str(downloads_path), recursive=False)
    
    print(f"👀 Watching: {downloads_path}")
    print("Press Ctrl+C to stop")
    
    observer.start()
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n✋ Stopped watching")
    observer.join()

def cmd_schedule(args):
    """Set up automatic cleaning schedule."""
    if args.remove:
        remove_schedule()
        print("📅 Schedule removed")
        return
    
    schedule_type = 'daily' if args.daily else 'weekly' if args.weekly else 'hourly'
    time_str = args.time or '09:00'
    
    success = setup_schedule(schedule_type, time_str)
    if success:
        print(f"📅 Scheduled {schedule_type} cleaning at {time_str}")
    else:
        print("❌ Failed to set up schedule")

def cmd_duplicates(args):
    """Find and manage duplicate files."""
    config = load_config()
    downloads_path = Path(args.path or config.get('downloads_path', '~/Downloads')).expanduser()
    
    cleaner = DownloadsCleaner(downloads_path, dry_run=not args.remove)
    duplicates = cleaner.find_duplicates()
    
    if not duplicates:
        print("✨ No duplicate files found!")
        return
    
    print(f"Found {len(duplicates)} sets of duplicates:\n")
    
    total_waste = 0
    for hash_val, file_list in duplicates.items():
        if len(file_list) > 1:
            sizes = [f.stat().st_size for f in file_list]
            wasted = sum(sizes[1:])  # All but one copy
            total_waste += wasted
            
            print(f"Duplicate set ({len(file_list)} files, {wasted/1024/1024:.2f} MB wasted):")
            for f in file_list:
                mod_time = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                print(f"  - {f.name} ({mod_time})")
            print()
    
    print(f"Total space wasted: {total_waste/1024/1024:.2f} MB")
    
    if args.remove:
        removed = cleaner.remove_duplicates(keep_newest=not args.keep_oldest)
        print(f"\n🗑️ Removed {removed} duplicate files")

def cmd_stats(args):
    """Show cleaning statistics."""
    stats_file = Path.home() / '.vibecleaner' / 'stats.json'
    
    if not stats_file.exists():
        print("No statistics available yet. Run 'vibecleaner clean' first.")
        return
    
    with open(stats_file) as f:
        stats = json.load(f)
    
    print("📊 VibeCleaner Statistics\n")
    print(f"Total operations: {stats.get('total_operations', 0)}")
    print(f"Files organized: {stats.get('files_moved', 0)}")
    print(f"Files deleted: {stats.get('files_deleted', 0)}")
    print(f"Duplicates removed: {stats.get('duplicates_removed', 0)}")
    print(f"Space freed: {stats.get('space_freed_mb', 0):.2f} MB")
    print(f"Last run: {stats.get('last_run', 'Never')}")

def cmd_config(args):
    """Edit or view configuration."""
    config_path = Path.home() / '.vibecleaner.yml'
    
    if args.edit:
        import subprocess
        import os
        editor = os.environ.get('EDITOR', 'nano' if sys.platform != 'win32' else 'notepad')
        subprocess.call([editor, str(config_path)])
    else:
        if config_path.exists():
            print(f"Configuration file: {config_path}\n")
            with open(config_path) as f:
                print(f.read())
        else:
            print("No configuration found. Run 'vibecleaner init' first.")

def main(argv=None):
    """VibeCleaner entry point."""
    parser = argparse.ArgumentParser(
        prog='vibecleaner',
        description='VibeCleaner - Smart Downloads Folder Organizer'
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize VibeCleaner')
    init_parser.add_argument('--force', action='store_true', help='Overwrite existing config')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean downloads folder')
    clean_parser.add_argument('--path', help='Path to downloads folder')
    clean_parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    clean_parser.add_argument('--no-organize', action='store_true', help='Skip file organization')
    clean_parser.add_argument('--duplicates', action='store_true', help='Remove duplicate files')
    clean_parser.add_argument('--remove-old', action='store_true', help='Remove old files')
    clean_parser.add_argument('--older-than', type=int, help='Days threshold for old files')
    clean_parser.add_argument('--log', help='Save operation log to file')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Watch folder for real-time organization')
    watch_parser.add_argument('path', nargs='?', help='Path to watch')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Set up automatic cleaning')
    schedule_parser.add_argument('--daily', action='store_true', help='Run daily')
    schedule_parser.add_argument('--weekly', action='store_true', help='Run weekly')
    schedule_parser.add_argument('--hourly', action='store_true', help='Run hourly')
    schedule_parser.add_argument('--time', help='Time to run (HH:MM)')
    schedule_parser.add_argument('--remove', action='store_true', help='Remove schedule')
    
    # Duplicates command
    dup_parser = subparsers.add_parser('duplicates', help='Find and manage duplicates')
    dup_parser.add_argument('--path', help='Path to scan')
    dup_parser.add_argument('--remove', action='store_true', help='Remove duplicates')
    dup_parser.add_argument('--keep-oldest', action='store_true', help='Keep oldest instead of newest')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='View or edit configuration')
    config_parser.add_argument('--edit', action='store_true', help='Open config in editor')
    
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to command handler
    cmd_map = {
        'init': cmd_init,
        'clean': cmd_clean,
        'watch': cmd_watch,
        'schedule': cmd_schedule,
        'duplicates': cmd_duplicates,
        'stats': cmd_stats,
        'config': cmd_config
    }
    
    handler = cmd_map.get(args.command)
    if handler:
        try:
            return handler(args) or 0
        except KeyboardInterrupt:
            print("\n⛔ Interrupted by user")
            return 1
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())