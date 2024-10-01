# Penjelasan Lengkap Bot Auto-Posting Telegram Pribadi

## Bagian-Bagian Penting Bot

- `src/auth.py`: Untuk masuk ke akun Telegram
- `src/cache.py`: Menyimpan data sementara agar bot lebih cepat
- `src/config.py`: Mengatur cara kerja bot
- `src/error_handler.py`: Menangani masalah yang mungkin terjadi
- `src/group_manager.py`: Mengatur grup-grup Telegram
- `src/logger.py`: Mencatat apa yang dilakukan bot
- `src/message_manager.py`: Mengatur pesan yang akan dikirim
- `src/message_sender.py`: Mengirim pesan ke grup
- `src/scheduler.py`: Mengatur jadwal pengiriman
- `src/utils.py`: Alat bantu lainnya

## Cara Mengatur Bot

- Gunakan `config.yaml` untuk mengatur bot secara umum
- Simpan data penting Telegram di file `.env`

## Cara Menggunakan

### Menambah Grup Baru
Tulis ID atau username grup di file `data/groups.txt`

### Mengubah Pesan yang Dikirim
Edit file pesan di folder yang Anda tentukan di `config.yaml`

## Jika Ada Masalah

- Lihat `logs/bot.log` untuk informasi umum
- Lihat `logs/bot.log.error` untuk masalah serius

## Menjaga Keamanan

- Jaga agar file `.env` dan `config.yaml` tetap rahasia
- Periksa apa yang dilakukan bot secara teratur

## Merawat Bot

- Bersihkan file log secara berkala
- Perbarui daftar grup dan pesan sesuai kebutuhan

## Ingat Selalu

Bot ini hanya untuk Anda dan orang terdekat. Gunakan dengan bijak dan sesuai aturan Telegram.
