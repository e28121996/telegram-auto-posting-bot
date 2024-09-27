# Folder Data

Folder ini berisi file-file penting untuk konfigurasi bot. Harap buat file-file berikut:

1. `groups.txt`: Daftar grup Telegram yang akan menerima pesan.
   Format: Satu username atau ID grup per baris.
   Contoh:
   ```
   @group1
   @group2
   -1001234567890
   ```

2. `blacklist.txt`: Daftar grup yang tidak akan menerima pesan.
   Format: Sama seperti groups.txt.

3. `pesan1.txt`, `pesan2.txt`, dst.: File-file berisi template pesan.
   Setiap file berisi satu template pesan lengkap.

PENTING: Jangan meng-commit atau membagikan file-file ini ke repositori publik karena berisi informasi sensitif.
