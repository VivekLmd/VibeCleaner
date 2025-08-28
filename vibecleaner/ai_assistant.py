"""AI-powered assistant for natural language cleaning commands."""

import json
import subprocess
import shlex
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .cleaner import DownloadsCleaner
from .config import load_config

class AICleanerAssistant:
    """AI assistant that understands natural language for file organization."""
    
    SYSTEM_PROMPT = """You are VibeCleaner AI, a helpful assistant that organizes Downloads folders.
    
    You understand natural language requests like:
    - "Clean up my downloads"
    - "Remove duplicate photos"
    - "Archive files older than 2 months"
    - "Organize my PDFs into Documents"
    - "Show me large files I can delete"
    - "What's taking up the most space?"
    
    Respond with specific actions and explain what you're doing in simple terms.
    Always prioritize safety - preview changes before executing them.
    """
    
    def __init__(self, provider: str = "claude"):
        """Initialize AI assistant with chosen provider."""
        self.provider = provider
        self.config = load_config()
        self.cleaner = None
        
    def process_request(self, user_request: str) -> Dict[str, Any]:
        """Process natural language request and execute appropriate actions."""
        
        # Build context-aware prompt
        prompt = self._build_prompt(user_request)
        
        # Get AI response
        response = self._call_ai_provider(prompt)
        
        # Parse AI response to extract actions
        actions = self._parse_ai_response(response)
        
        # Execute actions with user confirmation
        results = self._execute_actions(actions)
        
        return {
            'request': user_request,
            'ai_response': response,
            'actions': actions,
            'results': results
        }
    
    def _build_prompt(self, user_request: str) -> str:
        """Build context-aware prompt for AI."""
        
        # Get current downloads folder state
        downloads_path = Path(self.config.get('downloads_path', '~/Downloads')).expanduser()
        
        # Quick scan for context
        file_stats = self._scan_downloads_folder(downloads_path)
        
        prompt = f"""{self.SYSTEM_PROMPT}
        
Current Downloads Folder State:
- Total files: {file_stats['total_files']}
- Total size: {file_stats['total_size_mb']:.2f} MB
- File types: {', '.join(file_stats['file_types'][:10])}
- Oldest file: {file_stats['oldest_file_days']} days old
- Potential duplicates: {file_stats['potential_duplicates']}

User Request: "{user_request}"

Analyze this request and respond with:
1. Understanding of what the user wants
2. Specific actions to take (use these commands):
   - ORGANIZE: Sort files into category folders
   - REMOVE_OLD: Archive/delete old files (specify days)
   - REMOVE_DUPLICATES: Delete duplicate files
   - SCAN: Show statistics without changes
   - CUSTOM_RULE: Create specific organization rule
3. Safety considerations
4. Expected outcome

Format your response as JSON with these fields:
{{
    "understanding": "What I understand you want",
    "actions": [
        {{"type": "ACTION_TYPE", "parameters": {{}}, "description": "What this does"}}
    ],
    "safety_notes": "Important considerations",
    "expected_outcome": "What will happen"
}}
"""
        return prompt
    
    def _scan_downloads_folder(self, path: Path) -> Dict[str, Any]:
        """Quick scan of downloads folder for context."""
        if not path.exists():
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'file_types': [],
                'oldest_file_days': 0,
                'potential_duplicates': 0
            }
        
        from datetime import datetime
        import hashlib
        
        files = list(path.glob('*'))
        if not files:
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'file_types': [],
                'oldest_file_days': 0,
                'potential_duplicates': 0
            }
        
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        extensions = set(f.suffix.lower() for f in files if f.is_file() and f.suffix)
        
        oldest_time = min(f.stat().st_mtime for f in files if f.is_file())
        oldest_days = (datetime.now().timestamp() - oldest_time) / 86400
        
        # Quick duplicate check (same size files)
        size_map = {}
        for f in files:
            if f.is_file():
                size = f.stat().st_size
                size_map.setdefault(size, []).append(f)
        
        potential_dups = sum(len(files) - 1 for files in size_map.values() if len(files) > 1)
        
        return {
            'total_files': len([f for f in files if f.is_file()]),
            'total_size_mb': total_size / (1024 * 1024),
            'file_types': list(extensions),
            'oldest_file_days': int(oldest_days),
            'potential_duplicates': potential_dups
        }
    
    def _call_ai_provider(self, prompt: str) -> str:
        """Call AI provider (Claude or Codex) with prompt."""
        import os
        
        if self.provider == "claude":
            cmd = os.environ.get("VIBECLEANER_CLAUDE_CMD", "claude")
        else:
            cmd = os.environ.get("VIBECLEANER_CODEX_CMD", "codex")
        
        try:
            # Try to call the AI provider
            result = subprocess.run(
                shlex.split(cmd),
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                # Fallback to rule-based response if AI unavailable
                return self._fallback_response(prompt)
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Use rule-based fallback if provider not available
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Rule-based fallback when AI provider is unavailable."""
        user_request = prompt.split('User Request: "')[1].split('"')[0].lower()
        
        # Simple rule-based responses
        if "clean" in user_request or "organize" in user_request:
            return json.dumps({
                "understanding": "You want to organize your downloads folder",
                "actions": [
                    {"type": "ORGANIZE", "parameters": {}, "description": "Sort files into category folders"}
                ],
                "safety_notes": "Will preview changes first",
                "expected_outcome": "Files will be sorted into Documents, Images, Videos, etc."
            })
        
        elif "duplicate" in user_request:
            return json.dumps({
                "understanding": "You want to remove duplicate files",
                "actions": [
                    {"type": "REMOVE_DUPLICATES", "parameters": {"keep": "newest"}, 
                     "description": "Remove duplicate files, keeping newest versions"}
                ],
                "safety_notes": "Will show duplicates before deletion",
                "expected_outcome": "Duplicate files will be removed, freeing up space"
            })
        
        elif "old" in user_request or "archive" in user_request:
            days = 30  # Default
            for word in user_request.split():
                if word.isdigit():
                    days = int(word)
                    break
            
            return json.dumps({
                "understanding": f"You want to manage files older than {days} days",
                "actions": [
                    {"type": "REMOVE_OLD", "parameters": {"days": days}, 
                     "description": f"Archive files older than {days} days"}
                ],
                "safety_notes": "Old files will be moved to Archive folder, not deleted",
                "expected_outcome": f"Files older than {days} days will be archived"
            })
        
        else:
            return json.dumps({
                "understanding": "You want information about your downloads folder",
                "actions": [
                    {"type": "SCAN", "parameters": {}, "description": "Analyze downloads folder"}
                ],
                "safety_notes": "This is read-only, no changes will be made",
                "expected_outcome": "You'll see statistics about your downloads folder"
            })
    
    def _parse_ai_response(self, response: str) -> list:
        """Parse AI response to extract actionable commands."""
        try:
            # Try to parse as JSON
            data = json.loads(response)
            return data.get('actions', [])
        except json.JSONDecodeError:
            # Fallback to text parsing
            actions = []
            
            response_lower = response.lower()
            if "organize" in response_lower:
                actions.append({"type": "ORGANIZE", "parameters": {}})
            if "duplicate" in response_lower:
                actions.append({"type": "REMOVE_DUPLICATES", "parameters": {"keep": "newest"}})
            if "old" in response_lower or "archive" in response_lower:
                actions.append({"type": "REMOVE_OLD", "parameters": {"days": 30}})
            
            return actions if actions else [{"type": "SCAN", "parameters": {}}]
    
    def _execute_actions(self, actions: list) -> Dict[str, Any]:
        """Execute parsed actions with safety checks."""
        downloads_path = Path(self.config.get('downloads_path', '~/Downloads')).expanduser()
        self.cleaner = DownloadsCleaner(downloads_path, dry_run=True)
        
        results = {
            'executed': [],
            'preview': []
        }
        
        for action in actions:
            action_type = action.get('type')
            params = action.get('parameters', {})
            
            if action_type == 'ORGANIZE':
                organized = self.cleaner.organize_files()
                results['preview'].append({
                    'action': 'organize',
                    'details': organized
                })
                
            elif action_type == 'REMOVE_DUPLICATES':
                duplicates = self.cleaner.find_duplicates()
                results['preview'].append({
                    'action': 'remove_duplicates',
                    'details': f"Found {len(duplicates)} duplicate sets"
                })
                
            elif action_type == 'REMOVE_OLD':
                days = params.get('days', 30)
                old_files = self.cleaner.remove_old_files(days=days)
                results['preview'].append({
                    'action': 'archive_old',
                    'details': f"Found {len(old_files)} files older than {days} days"
                })
                
            elif action_type == 'SCAN':
                stats = self.cleaner.get_statistics()
                results['preview'].append({
                    'action': 'scan',
                    'details': stats
                })
        
        return results

class InteractiveAssistant:
    """Interactive chat-like interface for cleaning operations."""
    
    def __init__(self):
        self.assistant = AICleanerAssistant()
        self.conversation_history = []
        
    def chat(self, message: str) -> str:
        """Process chat message and return response."""
        
        # Process through AI assistant
        result = self.assistant.process_request(message)
        
        # Format response for user
        response = self._format_response(result)
        
        # Save to history
        self.conversation_history.append({
            'user': message,
            'assistant': response,
            'timestamp': str(datetime.now())
        })
        
        return response
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """Format AI result for user-friendly display."""
        lines = []
        
        # Parse AI understanding
        try:
            ai_data = json.loads(result['ai_response'])
            lines.append(f"✨ {ai_data.get('understanding', 'I understand your request')}")
            lines.append("")
            
            # Show planned actions
            if ai_data.get('actions'):
                lines.append("📋 Planned actions:")
                for action in ai_data['actions']:
                    lines.append(f"  • {action.get('description', action['type'])}")
                lines.append("")
            
            # Safety notes
            if ai_data.get('safety_notes'):
                lines.append(f"⚠️  {ai_data['safety_notes']}")
                lines.append("")
                
        except:
            lines.append("I'll help you organize your downloads folder.")
            lines.append("")
        
        # Show preview results
        if result.get('results', {}).get('preview'):
            lines.append("👀 Preview of changes:")
            for preview in result['results']['preview']:
                action = preview['action']
                details = preview['details']
                
                if action == 'organize' and isinstance(details, dict):
                    for category, files in details.items():
                        lines.append(f"  {category}: {len(files)} files")
                elif action == 'remove_duplicates':
                    lines.append(f"  {details}")
                elif action == 'archive_old':
                    lines.append(f"  {details}")
                elif action == 'scan' and isinstance(details, dict):
                    lines.append(f"  Total operations: {details.get('total_operations', 0)}")
                    lines.append(f"  Space that would be freed: {details.get('space_freed_mb', 0):.2f} MB")
        
        lines.append("")
        lines.append("💡 To execute these changes, use: vibecleaner clean --apply")
        lines.append("   Or continue chatting to refine the plan.")
        
        return "\n".join(lines)