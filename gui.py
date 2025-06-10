import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from mangadx_api import MangaDexAPI
from downloader import MangaDownloader
from utils import format_chapter_display

class MangaDexDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MangaDex Downloader")
        self.root.geometry("900x700")
        
        # Initialize API and downloader
        self.api = MangaDexAPI()
        self.downloader = MangaDownloader()
        
        # Data storage
        self.manga_results = []
        self.selected_manga = None
        self.chapter_results = []
        self.selected_chapter = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Search section
        search_frame = ttk.LabelFrame(main_frame, text="Search Manga", padding="10")
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.search_entry.bind('<Return>', lambda e: self.search_manga())
        
        self.search_btn = ttk.Button(search_frame, text="Search ALL", command=self.search_manga)
        self.search_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Language selection
        ttk.Label(search_frame, text="Languages:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.lang_var = tk.StringVar(value="en")
        lang_frame = ttk.Frame(search_frame)
        lang_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Radiobutton(lang_frame, text="English Only", variable=self.lang_var, value="en").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(lang_frame, text="All Languages", variable=self.lang_var, value="all").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Results section - two columns
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Manga results
        manga_frame = ttk.LabelFrame(results_frame, text="Manga Results", padding="5")
        manga_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        manga_frame.columnconfigure(0, weight=1)
        manga_frame.rowconfigure(0, weight=1)
        
        self.manga_listbox = tk.Listbox(manga_frame)
        self.manga_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.manga_listbox.bind('<<ListboxSelect>>', self.on_manga_select)
        
        manga_scrollbar = ttk.Scrollbar(manga_frame, orient=tk.VERTICAL, command=self.manga_listbox.yview)
        manga_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.manga_listbox.configure(yscrollcommand=manga_scrollbar.set)
        
        # Chapter results
        chapter_frame = ttk.LabelFrame(results_frame, text="Chapters", padding="5")
        chapter_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        chapter_frame.columnconfigure(0, weight=1)
        chapter_frame.rowconfigure(1, weight=1)
        
        # Chapter loading options
        options_frame = ttk.Frame(chapter_frame)
        options_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.load_all_btn = ttk.Button(options_frame, text="Load ALL Chapters (All Languages)", 
                                      command=self.load_all_chapters, state=tk.DISABLED)
        self.load_all_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Chapter count label
        self.chapter_count_label = ttk.Label(options_frame, text="", foreground="blue")
        self.chapter_count_label.grid(row=0, column=1)
        
        self.chapter_listbox = tk.Listbox(chapter_frame)
        self.chapter_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chapter_listbox.bind('<<ListboxSelect>>', self.on_chapter_select)
        
        chapter_scrollbar = ttk.Scrollbar(chapter_frame, orient=tk.VERTICAL, command=self.chapter_listbox.yview)
        chapter_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.chapter_listbox.configure(yscrollcommand=chapter_scrollbar.set)
        
        # Download section
        download_frame = ttk.LabelFrame(main_frame, text="Download", padding="10")
        download_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        download_frame.columnconfigure(0, weight=1)
        
        self.download_btn = ttk.Button(download_frame, text="Download Chapter", 
                                     command=self.download_chapter, state=tk.DISABLED)
        self.download_btn.grid(row=0, column=0, pady=(0, 10))
        
        # Progress section
        progress_frame = ttk.Frame(download_frame)
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
    
    def search_manga(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a manga title to search")
            return
        
        self.search_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text="Searching...")
        
        # Run search in separate thread
        thread = threading.Thread(target=self._search_manga_thread, args=(query,))
        thread.daemon = True
        thread.start()
    
    def _search_manga_thread(self, query):
        try:
            results = self.api.search_manga(query)
            self.manga_results = results
            
            # Update UI in main thread
            self.root.after(0, self._update_manga_results, results)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Search failed: {str(e)}")
    
    def _update_manga_results(self, results):
        self.manga_listbox.delete(0, tk.END)
        self.chapter_listbox.delete(0, tk.END)
        self.chapter_count_label.configure(text="")
        
        for manga in results:
            title = self.api.get_manga_title(manga)
            self.manga_listbox.insert(tk.END, title)
        
        self.search_btn.configure(state=tk.NORMAL)
        self.load_all_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text=f"Found {len(results)} manga")
    
    def on_manga_select(self, event):
        selection = self.manga_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.selected_manga = self.manga_results[index]
        manga_id = self.selected_manga['id']
        
        self.load_all_btn.configure(state=tk.NORMAL)
        self.status_label.configure(text="Loading ALL chapters (English only)...")
        
        # Load initial chapters in separate thread
        thread = threading.Thread(target=self._load_chapters_thread, args=(manga_id,))
        thread.daemon = True
        thread.start()
    
    def load_all_chapters(self):
        """Load ALL chapters for the selected manga in ALL languages"""
        if not self.selected_manga:
            return
            
        manga_id = self.selected_manga['id']
        self.load_all_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text="Loading ALL chapters in ALL languages... Please wait...")
        
        # Load all chapters in separate thread
        thread = threading.Thread(target=self._load_all_chapters_thread, args=(manga_id,))
        thread.daemon = True
        thread.start()
    
    def _load_chapters_thread(self, manga_id):
        try:
            # Load ALL chapters (English only by default)
            chapters = self.api.get_manga_chapters(manga_id)
            self.chapter_results = chapters
            
            # Update UI in main thread
            self.root.after(0, self._update_chapter_results, chapters, False)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Failed to load chapters: {str(e)}")
    
    def _load_all_chapters_thread(self, manga_id):
        try:
            chapters = self.api.get_all_manga_chapters(manga_id)
            self.chapter_results = chapters
            
            # Update UI in main thread
            self.root.after(0, self._update_chapter_results, chapters, True)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Failed to load all chapters: {str(e)}")
            self.root.after(0, lambda: self.load_all_btn.configure(state=tk.NORMAL))
    
    def _update_chapter_results(self, chapters, is_all_languages=False):
        self.chapter_listbox.delete(0, tk.END)
        
        for i, chapter in enumerate(chapters):
            attrs = chapter.get('attributes', {})
            display_text = format_chapter_display(attrs)
            
            # Add language info if multiple languages
            if is_all_languages:
                lang = attrs.get('translatedLanguage', 'unknown')
                display_text += f" [{lang.upper()}]"
            
            self.chapter_listbox.insert(tk.END, display_text)
        
        count_text = f"{len(chapters)} chapters loaded"
        if is_all_languages:
            count_text += " (All Languages)"
        else:
            count_text += " (English only - click button for more)"
            
        self.chapter_count_label.configure(text=count_text)
        self.status_label.configure(text=f"Loaded {len(chapters)} chapters")
        self.load_all_btn.configure(state=tk.NORMAL if not is_all_languages else tk.DISABLED)
    
    def on_chapter_select(self, event):
        selection = self.chapter_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_chapter = self.chapter_results[index]
            self.download_btn.configure(state=tk.NORMAL)
        else:
            self.download_btn.configure(state=tk.DISABLED)
    
    def download_chapter(self):
        if not self.selected_chapter or not self.selected_manga:
            messagebox.showwarning("Warning", "Please select a manga and chapter first")
            return
        
        # Ask for save directory
        save_dir = filedialog.askdirectory(title="Select Download Directory")
        if not save_dir:
            return
        
        manga_title = self.api.get_manga_title(self.selected_manga)
        
        self.download_btn.configure(state=tk.DISABLED)
        self.progress_var.set(0)
        
        # Start download in separate thread
        thread = threading.Thread(target=self._download_thread, 
                                args=(self.selected_chapter, manga_title, save_dir))
        thread.daemon = True
        thread.start()
    
    def _download_thread(self, chapter_data, manga_title, save_dir):
        try:
            def progress_callback(progress):
                self.root.after(0, lambda: self.progress_var.set(progress))
            
            def status_callback(status):
                self.root.after(0, lambda: self.status_label.configure(text=status))
            
            pdf_path = self.downloader.download_chapter(
                chapter_data, manga_title, save_dir,
                progress_callback, status_callback
            )
            
            self.root.after(0, self._download_complete, pdf_path)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Download failed: {str(e)}")
    
    def _download_complete(self, pdf_path):
        self.download_btn.configure(state=tk.NORMAL)
        self.status_label.configure(text="Download complete!")
        messagebox.showinfo("Success", f"Chapter downloaded successfully!\nSaved to: {pdf_path}")
    
    def _show_error(self, message):
        self.search_btn.configure(state=tk.NORMAL)
        self.download_btn.configure(state=tk.NORMAL if self.selected_chapter else tk.DISABLED)
        self.load_all_btn.configure(state=tk.NORMAL if self.selected_manga else tk.DISABLED)
        self.status_label.configure(text="Error occurred")
        messagebox.showerror("Error", message)

def main():
    root = tk.Tk()
    app = MangaDexDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()