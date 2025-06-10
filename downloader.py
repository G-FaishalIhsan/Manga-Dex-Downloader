import os
import io
import tempfile
from PIL import Image
import img2pdf
from mangadx_api import MangaDexAPI
from utils import sanitize_filename, save_to_history, create_directory_if_not_exists

class MangaDownloader:
    def __init__(self):
        self.api = MangaDexAPI()
    
    def download_chapter(self, chapter_data, manga_title, save_path, progress_callback=None, status_callback=None):
        """Download a complete chapter and save as PDF"""
        try:
            chapter_id = chapter_data['id']
            chapter_attrs = chapter_data.get('attributes', {})
            chapter_num = chapter_attrs.get('chapter', 'Unknown')
            
            if status_callback:
                status_callback(f"Getting page URLs for Chapter {chapter_num}...")
            
            # Get page URLs
            page_urls = self.api.get_chapter_pages(chapter_id)
            if not page_urls:
                raise Exception("No pages found for this chapter")
            
            if status_callback:
                status_callback(f"Found {len(page_urls)} pages. Starting download...")
            
            # Create temporary directory for images
            with tempfile.TemporaryDirectory() as temp_dir:
                image_files = []
                
                # Download all pages
                for i, url in enumerate(page_urls):
                    if status_callback:
                        status_callback(f"Downloading page {i+1}/{len(page_urls)}...")
                    
                    if progress_callback:
                        progress = int((i / len(page_urls)) * 80)  # 80% for download
                        progress_callback(progress)
                    
                    # Download page
                    page_data = self.api.download_page(url)
                    if page_data:
                        # Save temporary image file
                        page_filename = f"page_{i+1:03d}.jpg"
                        page_path = os.path.join(temp_dir, page_filename)
                        
                        try:
                            # Verify it's a valid image and convert if necessary
                            img = Image.open(io.BytesIO(page_data))
                            # Convert to RGB if necessary
                            if img.mode in ('RGBA', 'P'):
                                img = img.convert('RGB')
                            img.save(page_path, 'JPEG', quality=95)
                            image_files.append(page_path)
                        except Exception as e:
                            print(f"Error processing page {i+1}: {e}")
                            continue
                    else:
                        print(f"Failed to download page {i+1}")
                
                if not image_files:
                    raise Exception("No pages were successfully downloaded")
                
                if status_callback:
                    status_callback("Creating PDF...")
                
                if progress_callback:
                    progress_callback(90)
                
                # Create PDF filename
                safe_manga_title = sanitize_filename(manga_title)
                safe_chapter = sanitize_filename(str(chapter_num))
                pdf_filename = f"{safe_manga_title}_chapter_{safe_chapter}.pdf"
                pdf_path = os.path.join(save_path, pdf_filename)
                
                # Create PDF using img2pdf
                with open(pdf_path, "wb") as f:
                    f.write(img2pdf.convert(image_files))
                
                if progress_callback:
                    progress_callback(100)
                
                if status_callback:
                    status_callback(f"PDF saved: {pdf_filename}")
                
                # Save to history
                save_to_history(manga_title, chapter_num, pdf_path)
                
                return pdf_path
                
        except Exception as e:
            if status_callback:
                status_callback(f"Error: {str(e)}")
            raise e