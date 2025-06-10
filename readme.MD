# MangaDex Downloader

Aplikasi desktop untuk mengunduh manga dari MangaDex dengan GUI berbasis Tkinter.

## Fitur

- 🔍 Pencarian manga berdasarkan judul melalui API MangaDex v5
- 📚 Menampilkan hasil pencarian dalam daftar yang mudah dibaca
- 📖 Menampilkan daftar chapter untuk manga yang dipilih
- 📥 Download chapter dalam format PDF
- 📁 Pemilihan folder penyimpanan melalui dialog
- 📊 Progress bar dan status download real-time
- 📜 Riwayat download tersimpan dalam file JSON
- 🖼️ Konversi otomatis gambar ke PDF berkualitas tinggi

## Struktur File

```
mangadx-downloader/
├── gui.py              # GUI utama aplikasi
├── mangadx_api.py      # Wrapper API MangaDex
├── downloader.py       # Logic download dan konversi PDF
├── utils.py            # Fungsi utilitas
├── requirements.txt    # Dependencies
├── README.md          # Dokumentasi
└── history.json       # Log riwayat download (dibuat otomatis)
```

## Instalasi

1. **Clone atau download semua file ke folder yang sama**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi:**
   ```bash
   python gui.py
   ```

## Cara Penggunaan

1. **Pencarian Manga:**
   - Masukkan judul manga di kolom pencarian
   - Klik tombol "Search" atau tekan Enter
   - Hasil pencarian akan muncul di kolom kiri

2. **Pilih Manga:**
   - Klik pada manga yang diinginkan dari daftar hasil pencarian
   - Daftar chapter akan muncul di kolom kanan

3. **Download Chapter:**
   - Pilih chapter yang ingin didownload
   - Klik tombol "Download Chapter"
   - Pilih folder penyimpanan melalui dialog yang muncul
   - Tunggu proses download selesai

4. **Monitoring Progress:**
   - Progress bar menunjukkan kemajuan download
   - Status text memberikan informasi detail proses

## Dependencies

- `requests` - untuk HTTP requests ke API MangaDex
- `Pillow` (PIL) - untuk pemrosesan gambar
- `img2pdf` - untuk konversi gambar ke PDF
- `tkinter` - untuk GUI (sudah termasuk dalam Python)

## API yang Digunakan

Aplikasi ini menggunakan MangaDex API v5:
- `/manga` - untuk pencarian manga
- `/manga/{id}/feed` - untuk mendapatkan daftar chapter
- `/at-home/server/{chapterId}` - untuk mendapatkan URL gambar

## File Output

- **PDF Files:** Disimpan dengan format `[judul_manga]_chapter_[nomor].pdf`
- **History Log:** Tersimpan dalam `history.json` dengan informasi:
  - Judul manga
  - Nomor chapter
  - Path file PDF
  - Tanggal download

## Troubleshooting

### Error saat pencarian
- Pastikan koneksi internet stabil
- Coba kata kunci pencarian yang berbeda
- Beberapa manga mungkin tidak memiliki chapter dalam bahasa Inggris

### Error saat download
- Pastikan folder tujuan dapat ditulis
- Cek koneksi internet
- Beberapa chapter mungkin tidak memiliki gambar yang tersedia

### Error dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Catatan Penting

- Aplikasi ini hanya untuk penggunaan pribadi
- Hormati terms of service MangaDex
- Pastikan memiliki izin yang sesuai untuk konten yang didownload
- Beberapa manga mungkin memiliki pembatasan regional

## Kontribusi

Jika menemukan bug atau ingin menambahkan fitur:
1. Buat issue untuk bug report
2. Fork repository untuk pengembangan fitur
3. Submit pull request dengan deskripsi yang jelas