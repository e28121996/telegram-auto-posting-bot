# Bot Auto-Posting Telegram

Proyek ini adalah bot Telegram otomatis yang dirancang untuk mengirim pesan ke beberapa grup Telegram secara efisien dan aman, dengan mematuhi batasan dan aturan platform untuk menghindari penandaan sebagai spam.

**CATATAN PENTING: Proyek ini ditujukan untuk penggunaan pribadi dan terbatas. Harap gunakan dengan bertanggung jawab dan sesuai dengan Ketentuan Layanan Telegram.**

## Fitur

- Struktur modular untuk pemeliharaan dan integrasi fitur yang mudah
- Manajemen konfigurasi menggunakan Pydantic v2 dan YAML
- Autentikasi menggunakan akun Telegram pribadi
- Pengiriman pesan terjadwal dengan interval acak
- Pengiriman pesan massal dengan jeda acak
- Manajemen pesan dengan caching untuk meningkatkan kinerja
- Manajemen grup dengan fungsi blacklist
- Penanganan error yang komprehensif dengan notifikasi ke chat pribadi
- Sistem caching untuk mengoptimalkan kinerja
- Logging detail dengan rotasi dan manajemen log
- Operasi asinkron menggunakan asyncio

## Persiapan

1. Klon repositori:
   ```
   git clone https://github.com/e28121996/telegram-auto-posting-bot.git
   cd telegram-auto-posting-bot
   ```

2. Buat dan aktifkan lingkungan virtual:
   ```bash
   # Buat lingkungan virtual
   python -m venv venv

   # Aktifkan lingkungan virtual
   # Untuk Unix atau MacOS:
   source venv/bin/activate

   # Untuk Windows:
   # Command Prompt:
   venv\Scripts\activate.bat
   # PowerShell:
   venv\Scripts\Activate.ps1
   ```

   Catatan: Pastikan untuk menjalankan perintah yang sesuai dengan sistem operasi Anda.

3. Instal dependensi yang diperlukan:
   ```
   pip install -r requirements.txt
   ```

4. Buat file `.env` di direktori utama dan tambahkan kredensial API Telegram Anda:
   ```
   API_ID=api_id_anda
   API_HASH=api_hash_anda
   PHONE_NUMBER=nomor_telepon_anda
   PERSONAL_CHAT_ID=id_chat_pribadi_anda
   ```

5. Konfigurasikan file `config.yaml` sesuai dengan pengaturan yang Anda inginkan.

6. Siapkan folder `data/`:
   - Baca `data/README.md` untuk instruksi detail.
   - Buat file-file berikut berdasarkan contoh yang disediakan:
     - `groups.txt` (lihat `groups.example.txt`)
     - `blacklist.txt` (lihat `blacklist.example.txt`)
     - `pesan1.txt`, `pesan2.txt`, dst. (lihat `pesan1.example.txt`)

## Penggunaan

Jalankan bot menggunakan:

```
python main.py
```

## Dokumentasi Teknis

Untuk informasi lebih detail tentang arsitektur, modul, dan fungsi-fungsi utama, silakan lihat [Dokumentasi Teknis](DOCUMENTATION.md).

## Keamanan dan Privasi

- File-file dalam folder `data/` mengandung informasi sensitif dan tidak di-upload ke repositori.
- Pastikan untuk tidak membagikan atau meng-commit file-file dalam `data/` ke repositori publik.
- Selalu periksa `.gitignore` untuk memastikan file-file sensitif tidak akan di-track oleh Git.

## Peringatan

Bot ini menggunakan akun Telegram pribadi dan ditujukan untuk penggunaan pribadi atau terbatas. Penggunaan yang tidak bertanggung jawab dapat melanggar Ketentuan Layanan Telegram. Gunakan dengan bijak dan atas risiko Anda sendiri.

## Lisensi

[Lisensi MIT](LICENSE)
