import requests
import time

class MangaDexAPI:
    BASE_URL = "https://api.mangadex.org"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MangaDex Downloader/1.0'
        })
    
    def search_manga(self, title, get_all=True):
        """Search manga by title - get ALL results"""
        all_manga = []
        
        try:
            offset = 0
            limit = 100  # Max allowed by API
            
            while True:
                url = f"{self.BASE_URL}/manga"
                params = {
                    'title': title,
                    'limit': limit,
                    'offset': offset,
                    'includes[]': ['cover_art', 'author', 'artist'],
                    'availableTranslatedLanguage[]': ['en'],  # Bisa ditambah bahasa lain
                    'status[]': ['ongoing', 'completed', 'hiatus', 'cancelled'],
                    'contentRating[]': ['safe', 'suggestive', 'erotica']
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                manga_batch = data.get('data', [])
                
                if not manga_batch:
                    break
                
                all_manga.extend(manga_batch)
                
                # Check if we've got everything
                total = data.get('total', 0)
                if len(all_manga) >= total or len(manga_batch) < limit:
                    break
                
                offset += len(manga_batch)
                
                # Rate limiting
                time.sleep(0.1)
                
                # Don't get stuck in infinite loop
                if offset > 10000:  # Safety limit
                    print(f"Reached safety limit, got {len(all_manga)} manga")
                    break
            
            print(f"Found {len(all_manga)} manga total for '{title}'")
            return all_manga
            
        except Exception as e:
            print(f"Error searching manga: {e}")
            return all_manga  # Return what we have
    
    def get_manga_chapters(self, manga_id, get_all=True):
        """Get ALL chapters for a manga - no limits"""
        all_chapters = []
        
        try:
            offset = 0
            limit = 500  # Max allowed by API
            
            print(f"Loading chapters for manga {manga_id}...")
            
            while True:
                url = f"{self.BASE_URL}/manga/{manga_id}/feed"
                params = {
                    'limit': limit,
                    'offset': offset,
                    'order[chapter]': 'asc',
                    'translatedLanguage[]': ['en'],  # Bisa ditambah: ['en', 'id', 'ja', 'es', 'fr']
                    'contentRating[]': ['safe', 'suggestive', 'erotica', 'pornographic']
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                chapters = data.get('data', [])
                
                if not chapters:
                    break
                
                # Filter chapters - very permissive
                for chapter in chapters:
                    attrs = chapter.get('attributes', {})
                    pages = attrs.get('pages')
                    
                    # Accept almost all chapters
                    # Only exclude if explicitly marked as 0 pages AND has no external URL
                    if pages != 0 or attrs.get('externalUrl'):
                        all_chapters.append(chapter)
                
                print(f"Loaded {len(all_chapters)} chapters so far...")
                
                # Check if we're done
                total = data.get('total', 0)
                offset += len(chapters)
                
                if offset >= total or len(chapters) < limit:
                    break
                    
                # Rate limiting
                time.sleep(0.2)
                
                # Safety limit to prevent infinite loops
                if len(all_chapters) > 5000:
                    print(f"Reached safety limit of 5000 chapters")
                    break
            
            print(f"Total chapters loaded: {len(all_chapters)}")
            return all_chapters
            
        except Exception as e:
            print(f"Error getting chapters: {e}")
            return all_chapters
    
    def get_all_manga_chapters(self, manga_id, languages=['en', 'id', 'ja', 'es', 'fr', 'de', 'ru']):
        """Get ALL chapters for a manga in multiple languages - UNLIMITED"""
        all_chapters = []
        
        try:
            offset = 0
            limit = 500
            
            print(f"Loading ALL chapters (all languages) for manga {manga_id}...")
            
            while True:
                url = f"{self.BASE_URL}/manga/{manga_id}/feed"
                params = {
                    'limit': limit,
                    'offset': offset,
                    'order[chapter]': 'asc',
                    'translatedLanguage[]': languages,  # Multiple languages
                    'contentRating[]': ['safe', 'suggestive', 'erotica', 'pornographic']
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                chapters = data.get('data', [])
                
                if not chapters:
                    break
                
                # Accept ALL chapters regardless of page count
                all_chapters.extend(chapters)
                
                print(f"Loaded {len(all_chapters)} chapters so far...")
                
                # Check if we're done
                total = data.get('total', 0)
                offset += len(chapters)
                
                if offset >= total or len(chapters) < limit:
                    break
                    
                # Longer delay for more intensive requests
                time.sleep(0.3)
                
                # Higher safety limit for multi-language
                if len(all_chapters) > 10000:
                    print(f"Reached safety limit of 10,000 chapters")
                    break
            
            print(f"Total chapters loaded (all languages): {len(all_chapters)}")
            return all_chapters
            
        except Exception as e:
            print(f"Error getting all chapters: {e}")
            return all_chapters
    
    def get_chapter_pages(self, chapter_id):
        """Get page URLs for a chapter"""
        try:
            # First get the server info
            url = f"{self.BASE_URL}/at-home/server/{chapter_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            base_url = data.get('baseUrl')
            chapter_hash = data.get('chapter', {}).get('hash')
            pages = data.get('chapter', {}).get('data', [])
            
            if not all([base_url, chapter_hash, pages]):
                return []
            
            # Construct page URLs
            page_urls = []
            for page in pages:
                page_url = f"{base_url}/data/{chapter_hash}/{page}"
                page_urls.append(page_url)
            
            return page_urls
            
        except Exception as e:
            print(f"Error getting chapter pages: {e}")
            return []
    
    def download_page(self, url, timeout=30, retries=3):
        """Download a single page with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response.content
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for page {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    return None
    
    def get_manga_title(self, manga_data):
        """Extract manga title from manga data"""
        attributes = manga_data.get('attributes', {})
        title = attributes.get('title', {})
        
        # Try to get English title first
        if 'en' in title:
            return title['en']
        
        # If no English title, get the first available title
        if title:
            return list(title.values())[0]
        
        return "Unknown Title"