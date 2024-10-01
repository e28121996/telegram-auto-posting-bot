# Bot Auto-Posting Telegram Pribadi

Bot ini adalah alat otomatis yang Anda buat untuk mengirim pesan ke grup-grup Telegram secara terjadwal.

## Apa yang Bisa Dilakukan Bot Ini

- Mengirim pesan otomatis ke beberapa grup Telegram
- Mengatur jadwal pengiriman pesan
- Mengatur grup mana yang bisa dikirimi pesan dan mana yang tidak
- Menangani masalah saat mengirim pesan

## Cara Menyiapkan Bot

1. Pasang semua yang dibutuhkan: Ketik `pip install -r requirements.txt` di terminal
2. Buat file `.env` dan isi dengan data Telegram Anda
3. Atur `config.yaml` sesuai keinginan Anda

## Cara Menggunakan Bot

Jalankan bot dengan mengetik: `python main.py` di terminal

## Isi Folder Proyek

- `main.py`: Program utama
- `src/`: Berisi bagian-bagian penting bot
- `config.yaml`: Tempat mengatur bot
- `data/`: Berisi daftar grup dan pesan
- `logs/`: Berisi catatan apa yang dilakukan bot

## Penting Diingat

Bot ini hanya untuk penggunaan pribadi dan terbatas. Pastikan penggunaan sesuai dengan Ketentuan Layanan Telegram.

## Jika Ada Masalah

Lihat file di folder `logs/` untuk tahu apa yang terjadi jika ada masalah.
