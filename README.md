# VibeCleaner — Smart Downloads Folder Organizer

## About

**VibeCleaner** is an intelligent automation tool that keeps your Downloads folder clean and organized. It automatically sorts files, removes clutter, and maintains a tidy file system without manual intervention.

### 🎯 What VibeCleaner Does

VibeCleaner transforms your chaotic Downloads folder into an organized file system by:

- **Auto-Organization**: Sorts files into categorized folders (Documents, Images, Videos, Archives, etc.)
- **Duplicate Detection**: Identifies and removes duplicate files to save disk space
- **Old File Management**: Archives or deletes files older than specified periods
- **Smart Filtering**: Recognizes file patterns and sorts based on customizable rules
- **Safe Operations**: Dry-run mode shows what will happen before making changes

### ✨ Key Features

- **File Type Recognition**: Automatically categorizes files by extension and content
  - Documents (PDF, DOCX, TXT, etc.)
  - Images (JPG, PNG, GIF, etc.)
  - Videos (MP4, AVI, MKV, etc.)
  - Archives (ZIP, RAR, 7Z, etc.)
  - Code files (PY, JS, HTML, etc.)
  - Audio (MP3, WAV, FLAC, etc.)

- **Intelligent Rules Engine**:
  - Move files based on age
  - Sort by file size thresholds
  - Custom naming patterns
  - Subfolder organization by date

- **Safety Features**:
  - Preview mode to see changes before execution
  - Undo functionality for recent operations
  - Whitelist important files
  - Backup before deletion option

- **Scheduling Options**:
  - Run on system startup
  - Periodic cleaning (hourly, daily, weekly)
  - Watch folder for real-time organization
  - Manual trigger via CLI or GUI

### 📋 Use Cases

- **Daily Cleanup**: Automatically organize downloads every day
- **Project Files**: Sort project files into dedicated folders
- **Media Management**: Organize photos and videos by date
- **Document Filing**: Keep documents sorted by type and date
- **Disk Space Recovery**: Remove old and duplicate files
- **Download History**: Maintain organized archive of downloads

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install vibecleaner

# Or install from source
git clone https://github.com/yourusername/vibecleaner.git
cd vibecleaner
pip install .
```

### Basic Usage

```bash
# Initialize VibeCleaner with default settings
vibecleaner init

# Preview what will be cleaned (dry run)
vibecleaner clean --dry-run

# Clean downloads folder
vibecleaner clean

# Clean with specific rules
vibecleaner clean --older-than 30d --duplicates

# Watch folder for real-time organization
vibecleaner watch ~/Downloads

# Schedule automatic cleaning
vibecleaner schedule --daily --time 09:00
```

### Configuration

Create a `.vibecleaner.yml` in your home directory:

```yaml
# Download folder path (default: ~/Downloads)
downloads_path: ~/Downloads

# Organization rules
organize:
  Documents:
    extensions: [pdf, doc, docx, txt, odt]
    path: ~/Documents/Downloads
  Images:
    extensions: [jpg, jpeg, png, gif, svg, webp]
    path: ~/Pictures/Downloads
  Videos:
    extensions: [mp4, avi, mkv, mov, wmv]
    path: ~/Videos/Downloads
  Archives:
    extensions: [zip, rar, 7z, tar, gz]
    path: ~/Downloads/Archives

# Cleanup rules
cleanup:
  delete_after_days: 90
  archive_after_days: 30
  min_file_size: 1MB  # Ignore small files
  remove_duplicates: true
  
# Safety settings
safety:
  dry_run_default: true
  backup_before_delete: true
  whitelist_patterns:
    - "important_*"
    - "*.key"
    - "*.license"
```

## 🛠️ Advanced Features

### Custom Rules

```bash
# Add custom organization rule
vibecleaner rule add --name "Screenshots" \
  --pattern "Screen Shot*" \
  --destination ~/Pictures/Screenshots

# Remove old downloads
vibecleaner clean --older-than 60d --min-size 100MB

# Find and remove duplicates
vibecleaner duplicates --remove --keep-newest
```

### Scheduling (Cross-platform)

```bash
# Linux/Mac: Add to crontab
vibecleaner schedule --cron "0 9 * * *"

# Windows: Add to Task Scheduler  
vibecleaner schedule --windows --daily --time 09:00

# Run as daemon/service
vibecleaner daemon start
```

## 📊 Statistics & Reports

```bash
# Show cleaning statistics
vibecleaner stats

# Generate cleaning report
vibecleaner report --last-30-days

# Show disk space saved
vibecleaner savings
```

## 🔧 Command Reference

| Command | Description |
|---------|-------------|
| `vibecleaner init` | Initialize configuration |
| `vibecleaner clean` | Clean downloads folder |
| `vibecleaner watch` | Watch folder for real-time organization |
| `vibecleaner schedule` | Set up automatic cleaning |
| `vibecleaner undo` | Undo last cleaning operation |
| `vibecleaner stats` | Show cleaning statistics |
| `vibecleaner config` | Edit configuration |

## 🛡️ Safety & Privacy

- **No Cloud Dependency**: Works entirely offline
- **Local Processing**: Your files never leave your machine
- **Transparent Operations**: Full logs of all actions
- **Reversible Changes**: Undo support for recent operations
- **No Data Collection**: Zero telemetry or analytics

## 📝 License

Licensed under the MIT License. See the `LICENSE` file for details.

## 🤝 Contributing

Contributions are welcome! See `CONTRIBUTING.md` for guidelines.

## 💡 Tips

- Start with `--dry-run` to preview changes
- Use `--verbose` for detailed operation logs
- Set up whitelists for important files
- Regular backups recommended before major cleanups
- Test custom rules on a sample folder first

---

**Note**: VibeCleaner respects your system's Recycle Bin/Trash settings by default. Deleted files can be recovered from trash unless explicitly purged.