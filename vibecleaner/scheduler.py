"""Scheduler for automatic cleaning operations."""

import sys
import subprocess
from pathlib import Path

def setup_schedule(schedule_type: str, time_str: str) -> bool:
    """Set up automatic scheduling based on OS."""
    if sys.platform == 'win32':
        return setup_windows_schedule(schedule_type, time_str)
    elif sys.platform == 'darwin':
        return setup_macos_schedule(schedule_type, time_str)
    else:
        return setup_linux_schedule(schedule_type, time_str)

def remove_schedule() -> bool:
    """Remove automatic scheduling."""
    if sys.platform == 'win32':
        return remove_windows_schedule()
    elif sys.platform == 'darwin':
        return remove_macos_schedule()
    else:
        return remove_linux_schedule()

def setup_windows_schedule(schedule_type: str, time_str: str) -> bool:
    """Set up Windows Task Scheduler."""
    try:
        task_name = "VibeCleaner"
        vibecleaner_path = sys.executable.replace('python.exe', 'Scripts\\vibecleaner.exe')
        
        # Remove existing task if present
        subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], 
                      capture_output=True)
        
        # Create new task
        if schedule_type == 'daily':
            cmd = [
                'schtasks', '/create',
                '/tn', task_name,
                '/tr', f'"{vibecleaner_path}" clean',
                '/sc', 'daily',
                '/st', time_str,
                '/f'
            ]
        elif schedule_type == 'weekly':
            cmd = [
                'schtasks', '/create',
                '/tn', task_name,
                '/tr', f'"{vibecleaner_path}" clean',
                '/sc', 'weekly',
                '/st', time_str,
                '/f'
            ]
        else:  # hourly
            cmd = [
                'schtasks', '/create',
                '/tn', task_name,
                '/tr', f'"{vibecleaner_path}" clean',
                '/sc', 'hourly',
                '/f'
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def setup_linux_schedule(schedule_type: str, time_str: str) -> bool:
    """Set up cron job on Linux."""
    try:
        # Get current crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""
        
        # Remove existing VibeCleaner entries
        lines = [l for l in current_cron.split('\n') 
                if 'vibecleaner clean' not in l and l.strip()]
        
        # Add new entry
        if schedule_type == 'daily':
            hour, minute = time_str.split(':')
            lines.append(f"{minute} {hour} * * * vibecleaner clean")
        elif schedule_type == 'weekly':
            hour, minute = time_str.split(':')
            lines.append(f"{minute} {hour} * * 0 vibecleaner clean")
        else:  # hourly
            lines.append("0 * * * * vibecleaner clean")
        
        # Write new crontab
        new_cron = '\n'.join(lines) + '\n'
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(new_cron)
        
        return process.returncode == 0
    except Exception:
        return False

def setup_macos_schedule(schedule_type: str, time_str: str) -> bool:
    """Set up launchd job on macOS."""
    try:
        plist_path = Path.home() / 'Library' / 'LaunchAgents' / 'com.vibecleaner.plist'
        plist_path.parent.mkdir(exist_ok=True)
        
        if schedule_type == 'daily':
            hour, minute = time_str.split(':')
            calendar_interval = f"""
        <key>StartCalendarInterval</key>
        <dict>
            <key>Hour</key>
            <integer>{hour}</integer>
            <key>Minute</key>
            <integer>{minute}</integer>
        </dict>"""
        elif schedule_type == 'weekly':
            hour, minute = time_str.split(':')
            calendar_interval = f"""
        <key>StartCalendarInterval</key>
        <dict>
            <key>Weekday</key>
            <integer>0</integer>
            <key>Hour</key>
            <integer>{hour}</integer>
            <key>Minute</key>
            <integer>{minute}</integer>
        </dict>"""
        else:  # hourly
            calendar_interval = """
        <key>StartInterval</key>
        <integer>3600</integer>"""
        
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vibecleaner</string>
    <key>ProgramArguments</key>
    <array>
        <string>vibecleaner</string>
        <string>clean</string>
    </array>
    {calendar_interval}
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>"""
        
        plist_path.write_text(plist_content)
        
        # Load the job
        subprocess.run(['launchctl', 'unload', str(plist_path)], capture_output=True)
        result = subprocess.run(['launchctl', 'load', str(plist_path)], capture_output=True)
        
        return result.returncode == 0
    except Exception:
        return False

def remove_windows_schedule() -> bool:
    """Remove Windows Task Scheduler job."""
    try:
        result = subprocess.run(['schtasks', '/delete', '/tn', 'VibeCleaner', '/f'], 
                              capture_output=True)
        return result.returncode == 0
    except Exception:
        return False

def remove_linux_schedule() -> bool:
    """Remove cron job on Linux."""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode != 0:
            return True
        
        current_cron = result.stdout
        lines = [l for l in current_cron.split('\n') 
                if 'vibecleaner clean' not in l and l.strip()]
        
        new_cron = '\n'.join(lines) + '\n' if lines else ''
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(new_cron)
        
        return process.returncode == 0
    except Exception:
        return False

def remove_macos_schedule() -> bool:
    """Remove launchd job on macOS."""
    try:
        plist_path = Path.home() / 'Library' / 'LaunchAgents' / 'com.vibecleaner.plist'
        
        if plist_path.exists():
            subprocess.run(['launchctl', 'unload', str(plist_path)], capture_output=True)
            plist_path.unlink()
        
        return True
    except Exception:
        return False