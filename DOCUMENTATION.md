# Dokumentasi Teknis Bot Auto-Posting Telegram

## Struktur Proyek

- `main.py`: Script utama untuk menjalankan bot.
- `src/`: Direktori berisi modul-modul bot.
  - `auth.py`: Modul autentikasi Telegram.
  - `cache.py`: Implementasi sistem cache.
  - `config.py`: Manajemen konfigurasi.
  - `error_handler.py`: Penanganan error dan notifikasi.
  - `group_manager.py`: Manajemen grup dan blacklist.
  - `logger.py`: Konfigurasi dan setup logging.
  - `message_manager.py`: Manajemen pesan dan template.
  - `message_sender.py`: Fungsi pengiriman pesan.
  - `scheduler.py`: Penjadwalan tugas.
  - `utils.py`: Fungsi-fungsi utilitas.

## Modul Utama

### main.py

- `send_scheduled_messages(client: TelegramClient) -> None`:
  Mengirim pesan terjadwal ke grup-grup yang valid.

- `clear_cache_periodically() -> None`:
  Membersihkan entri cache yang kadaluarsa secara berkala.

- `main() -> None`:
  Fungsi utama yang menjalankan loop bot.

### src/auth.py

- `create_client() -> TelegramClient`:
  Membuat dan mengautentikasi client Telegram.

### src/cache.py

- `class Cache(Generic[T])`:
  Implementasi cache dengan waktu kadaluarsa.
  - `set(key: str, value: T, expiry: int = 3600) -> None`
  - `get(key: str) -> Union[T, None]`
  - `clear_expired() -> None`

### src/config.py

- `class Settings(BaseSettings)`:
  Kelas untuk menyimpan nilai konfigurasi.

- `load_yaml_config(file_path: str = "config.yaml") -> Dict[str, Any]`:
  Memuat konfigurasi dari file YAML.

### src/error_handler.py

- `handle_sending_error(error: Exception, group: str, message: str, retry_count: int = 0) -> Optional[str]`:
  Menangani error yang terjadi saat pengiriman pesan.

- `handle_scheduler_error(error: Exception) -> None`:
  Menangani error yang terjadi selama penjadwalan.

- `send_critical_error_notification(client: TelegramClient, error_message: str) -> None`:
  Mengirim notifikasi error kritis ke chat pribadi.

### src/group_manager.py

- `class GroupManager`:
  Mengelola grup dan blacklist.
  - `load_groups() -> List[str]`
  - `load_blacklist() -> List[str]`
  - `get_valid_groups() -> List[str]`
  - `add_to_blacklist(group: str) -> None`

### src/message_manager.py

- `class MessageManager`:
  Mengelola template pesan.
  - `load_message(file_path: str) -> str`
  - `get_random_message() -> str`
  - `get_appropriate_message(group_rules: Dict[str, Any]) -> str`

### src/message_sender.py

- `send_message(client: TelegramClient, group: str, message: str) -> None`:
  Mengirim pesan ke grup tertentu.

- `send_mass_message(client: TelegramClient, groups: List[str], message: str) -> None`:
  Mengirim pesan ke beberapa grup.

### src/scheduler.py

- `class Scheduler`:
  Mengelola penjadwalan tugas.
  - `schedule_task(task: Callable, min_interval: float = 1.3, max_interval: float = 1.5) -> None`
  - `add_task(task: Callable) -> None`
  - `run() -> None`

## Alur Kerja Bot

1. Bot dimulai dengan menjalankan `main.py`.
2. Autentikasi client Telegram dilakukan melalui `create_client()`.
3. Scheduler diinisialisasi dan tugas pengiriman pesan dijadwalkan.
4. Pada interval yang ditentukan, bot akan:
   - Memuat daftar grup valid.
   - Memilih pesan acak.
   - Mengirim pesan ke setiap grup dengan jeda acak.
5. Error ditangani dan dicatat, dengan grup bermasalah ditambahkan ke blacklist.
6. Error kritis dikirim sebagai notifikasi ke chat pribadi.
7. Cache dibersihkan secara berkala untuk mengoptimalkan penggunaan memori.

## Konfigurasi

Konfigurasi bot diatur melalui file `config.yaml` dan variabel lingkungan dalam `.env`.

## Logging

Log disimpan di direktori `logs/` dengan rotasi harian dan pembatasan ukuran file.

## Keamanan

- Kredensial disimpan dalam file `.env` yang tidak di-track oleh Git.
- Sesi Telegram disimpan secara lokal dan tidak di-upload ke repositori.
- Notifikasi error kritis dikirim ke chat pribadi untuk keamanan tambahan.

## Pengembangan Lebih Lanjut

- Implementasi sistem notifikasi yang lebih canggih.
- Penambahan antarmuka admin untuk manajemen bot.
- Peningkatan sistem caching untuk mendukung penyimpanan persisten.
- Implementasi mekanisme retry yang lebih canggih untuk error tertentu.
