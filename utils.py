import json
import os
import re
from datetime import datetime

def sanitize_filename(filename):
    """Sanitize filename to be safe for filesystem"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and dots
    filename = re.sub(r'\.+$', '', filename.strip())
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def save_to_history(manga_title, chapter_number, file_path):
    """Save download history to JSON file"""
    history_file = "history.json"
    
    # Load existing history
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    # Add new entry
    entry = {
        "manga_title": manga_title,
        "chapter_number": chapter_number,
        "file_path": file_path,
        "download_date": datetime.now().isoformat()
    }
    
    history.append(entry)
    
    # Save updated history
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")

def create_directory_if_not_exists(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)

def format_chapter_display(chapter):
    """Format chapter for display in listbox with enhanced info"""
    chapter_num = chapter.get('chapter', 'N/A')
    title = chapter.get('title', '')
    volume = chapter.get('volume', '')
    pages = chapter.get('pages', 'Unknown')
    language = chapter.get('translatedLanguage', 'unknown')
    
    # Build display string
    display_parts = []
    
    # Volume info
    if volume:
        display_parts.append(f"Vol.{volume}")
    
    # Chapter info
    display_parts.append(f"Ch.{chapter_num}")
    
    # Title
    if title:
        display_parts.append(f": {title}")
    
    # Page count
    if pages != 'Unknown' and pages is not None:
        display_parts.append(f" ({pages}p)")
    
    # Language (if not English)
    if language != 'en':
        display_parts.append(f" [{language.upper()}]")
    
    return ''.join(display_parts)

def get_language_name(code):
    """Convert language code to readable name"""
    languages = {
        'en': 'English',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'id': 'Indonesian',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'ru': 'Russian',
        'pt': 'Portuguese',
        'it': 'Italian',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'ar': 'Arabic',
        'tr': 'Turkish'
    }
    return languages.get(code, code.upper())