# Bot Auto-Posting Telegram

Proyek ini adalah bot Telegram otomatis yang dirancang untuk mengirim pesan ke beberapa grup Telegram secara efisien dan aman, dengan mematuhi batasan dan aturan platform untuk menghindari penandaan sebagai spam.

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
   git clone https://github.com/username-anda/bot-auto-posting-telegram.git
   cd bot-auto-posting-telegram
   ```

2. Buat lingkungan virtual dan aktifkan:
   ```
   python -m venv venv
   source venv/bin/activate  # Pada Windows, gunakan `venv\Scripts\activate`
   ```

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

6. Tambahkan grup Anda ke `data/groups.txt` dan grup yang di-blacklist ke `data/blacklist.txt`.

7. Tambahkan template pesan Anda ke `data/pesan1.txt`, `data/pesan2.txt`, dst.

## Penggunaan

Jalankan bot menggunakan:

```
python main.py
```

## Dokumentasi Teknis

Untuk informasi lebih detail tentang arsitektur, modul, dan fungsi-fungsi utama, silakan lihat [Dokumentasi Teknis](DOCUMENTATION.md).

## Peringatan

Bot ini menggunakan akun Telegram pribadi. Berhati-hatilah untuk tidak melanggar ketentuan layanan atau kebijakan spam Telegram. Gunakan dengan bertanggung jawab dan atas risiko Anda sendiri.

## Lisensi

[Lisensi MIT](LICENSE)
