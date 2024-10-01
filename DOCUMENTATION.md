# Dokumentasi Bot Auto-Posting Telegram Pribadi

## Modul-modul Utama

### src/auth.py
Menangani proses autentikasi dengan API Telegram.
- `create_client()`: Membuat dan mengautentikasi klien Telegram.

### src/cache.py
Implementasi sistem cache untuk meningkatkan kinerja.
- Kelas `Cache`: Menyediakan mekanisme caching dengan waktu kedaluwarsa.

### src/config.py
Mengelola konfigurasi dari file YAML dan variabel lingkungan.
- `get_config()`: Mengambil nilai konfigurasi.

### src/error_handler.py
Menangani berbagai jenis kesalahan yang mungkin terjadi.
- `handle_sending_error()`: Menangani kesalahan saat mengirim pesan.
- `send_critical_error_notification()`: Mengirim notifikasi untuk kesalahan kritis.

### src/group_manager.py
Mengelola grup Telegram, termasuk daftar hitam dan informasi mode lambat.
- Kelas `GroupManager`: Menyediakan metode untuk memuat dan mengelola grup.

### src/logger.py
Konfigurasi dan setup untuk sistem logging aplikasi.

### src/message_manager.py
Mengelola pesan yang akan dikirim.
- Kelas `MessageManager`: Memilih dan memformat pesan berdasarkan aturan grup.

### src/message_sender.py
Menangani pengiriman pesan ke grup.
- `send_message()`: Mengirim pesan ke satu grup.
- `send_mass_message()`: Mengirim pesan ke beberapa grup.

### src/scheduler.py
Mengatur penjadwalan pengiriman pesan.
- Kelas `Scheduler`: Mengelola tugas-tugas terjadwal.

### src/utils.py
Berisi fungsi-fungsi utilitas yang digunakan di seluruh aplikasi.

## Konfigurasi

### config.yaml
File ini berisi konfigurasi utama bot. Beberapa pengaturan penting meliputi:
- Direktori data dan log
- Pengaturan pengiriman pesan (delay, interval)
- Pengaturan cache
- Opsi debug

### .env
File ini harus berisi kredensial sensitif:
- `API_ID`: ID API Telegram Anda
- `API_HASH`: Hash API Telegram Anda
- `PHONE_NUMBER`: Nomor telepon yang terkait dengan akun Telegram Anda
- `PERSONAL_CHAT_ID`: ID chat pribadi untuk menerima notifikasi

## Penggunaan Lanjutan

### Menambahkan Grup Baru
Untuk menambahkan grup baru, tambahkan ID atau username grup ke file `data/groups.txt`.

### Mengubah Pesan
Pesan-pesan yang akan dikirim disimpan dalam file-file di direktori yang ditentukan dalam `config.yaml`. Anda dapat mengedit file-file ini untuk mengubah konten pesan.

### Penanganan Kesalahan
Bot dilengkapi dengan sistem penanganan kesalahan yang komprehensif. Kesalahan kritis akan dikirimkan ke chat pribadi yang ditentukan di `PERSONAL_CHAT_ID`.

### Optimasi Kinerja
Gunakan pengaturan cache di `config.yaml` untuk mengoptimalkan kinerja, terutama jika mengelola banyak grup.

## Pemecahan Masalah

- Jika bot gagal terhubung, periksa kredensial di file `.env`.
- Untuk masalah pengiriman pesan, periksa log di `logs/bot.log` untuk informasi lebih lanjut.
- Jika ada grup yang selalu dilewati, periksa apakah grup tersebut ada dalam daftar hitam di `data/blacklist.txt`.
- Jika bot tiba-tiba berhenti bekerja, periksa `logs/bot.log.error` untuk informasi tentang kesalahan kritis.

## Keamanan dan Privasi

- Pastikan file `.env` dan `config.yaml` tidak dapat diakses oleh pihak yang tidak berwenang.
- Jangan bagikan kredensial API Telegram Anda dengan siapa pun.
- Secara berkala, periksa aktivitas bot untuk memastikan tidak ada penggunaan yang tidak sah.

## Pemeliharaan

- Secara berkala, bersihkan file log untuk menghemat ruang penyimpanan.
- Perbarui daftar grup dan pesan secara teratur untuk memastikan relevansi.
- Pantau penggunaan API Telegram Anda untuk menghindari pembatasan atau pemblokiran.

## Catatan Penting

Bot ini dirancang untuk penggunaan pribadi. Pastikan untuk mematuhi Ketentuan Layanan Telegram dan tidak menggunakan bot untuk spam atau aktivitas yang melanggar aturan.
