# Bot Auto-Posting Telegram Pribadi

Bot ini adalah alat otomatis pribadi untuk mengirim pesan ke berbagai grup Telegram secara terjadwal.

## Fitur Utama

- Pengiriman pesan otomatis ke beberapa grup Telegram
- Penjadwalan pengiriman pesan dengan interval yang dapat dikonfigurasi
- Manajemen grup termasuk daftar hitam dan penanganan mode lambat (slow mode)
- Caching untuk meningkatkan kinerja
- Penanganan kesalahan dan notifikasi
- Konfigurasi yang fleksibel melalui file YAML dan variabel lingkungan
- Profiling untuk analisis kinerja

## Persyaratan

- Python 3.7+
- Telethon
- PyYAML
- python-dotenv
- Pydantic

## Pengaturan

1. Pastikan semua dependensi terinstal:
   ```
   pip install -r requirements.txt
   ```

2. Buat file `.env` di direktori utama proyek dan isi dengan kredensial Telegram Anda:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   PHONE_NUMBER=your_phone_number
   PERSONAL_CHAT_ID=your_personal_chat_id
   ```
   Ganti nilai-nilai tersebut dengan kredensial Telegram Anda yang sesuai.

3. Edit `config.yaml` sesuai kebutuhan Anda.

## Penggunaan

1. Pastikan semua konfigurasi sudah benar di file `.env` dan `config.yaml`.

2. Jalankan bot dengan perintah:
   ```
   python main.py
   ```

3. Bot akan mulai berjalan dan mengirim pesan sesuai jadwal yang telah dikonfigurasi.

## Struktur Proyek

- `main.py`: Skrip utama untuk menjalankan bot
- `src/`: Direktori berisi modul-modul utama bot
- `config.yaml`: File konfigurasi utama
- `.env`: File untuk menyimpan kredensial dan konfigurasi sensitif
- `data/`: Direktori untuk menyimpan data seperti daftar grup dan pesan
- `logs/`: Direktori untuk file log

## Konfigurasi

Lihat `config.yaml` untuk opsi konfigurasi yang tersedia. Kredensial sensitif disimpan di file `.env`.

## Penanganan Kesalahan dan Logging

Bot dilengkapi dengan sistem logging. Cek file `logs/bot.log` untuk informasi detail tentang operasi bot dan `logs/bot.log.error` untuk log kesalahan. Kesalahan kritis akan dikirimkan ke chat pribadi yang ditentukan di `PERSONAL_CHAT_ID`.

## Fitur Tambahan

- **Slow Mode Maintenance**: Bot secara otomatis membersihkan informasi slow mode dan menyimpan statistiknya setiap jam.
- **Dynamic Scheduling**: Interval pengiriman pesan disesuaikan secara dinamis berdasarkan tingkat keberhasilan dan kegagalan.
- **Profiling**: Bot menggunakan cProfile untuk menganalisis kinerja dan mencatat hasil profiling di log.

## Catatan Penting

Bot ini dirancang untuk penggunaan pribadi. Pastikan untuk mematuhi Ketentuan Layanan Telegram dan tidak menggunakan bot untuk spam atau aktivitas yang melanggar aturan.

## Pemecahan Masalah

Jika mengalami masalah saat menjalankan bot, periksa file log untuk informasi lebih lanjut atau lihat bagian Pemecahan Masalah di [DOCUMENTATION.md](DOCUMENTATION.md).

## Dokumentasi

Untuk informasi lebih lanjut tentang cara kerja bot dan detail implementasi, lihat [DOCUMENTATION.md](DOCUMENTATION.md).

## Lisensi

[MIT License](LICENSE)

## Pemecahan Masalah

Jika Anda mengalami masalah saat menjalankan bot, silakan periksa bagian Pemecahan Masalah di [DOCUMENTATION.md](DOCUMENTATION.md) untuk panduan lebih lanjut.
