# Codex Local Backup

Backup ini dibuat untuk mencegah kehilangan konteks chat Codex ketika ganti akun, reinstall, atau state lokal rusak.

## Backup Manual

Jalankan dari root project:

```powershell
powershell -ExecutionPolicy Bypass -File .\Scripts\backup_codex_data.ps1
```

Hasil backup akan masuk ke:

```text
Codex_Backups\
```

Script akan membuat folder snapshot dan file zip bertimestamp.

## Backup Otomatis Harian

Pasang Windows Scheduled Task:

```powershell
powershell -ExecutionPolicy Bypass -File .\Scripts\install_codex_backup_task.ps1
```

Default jadwalnya mulai pukul `00:00` dan berulang setiap `24` jam. Untuk backup setiap 3 jam:

```powershell
powershell -ExecutionPolicy Bypass -File .\Scripts\install_codex_backup_task.ps1 -EveryHours 3
```

Untuk mulai dari jam tertentu:

```powershell
powershell -ExecutionPolicy Bypass -File .\Scripts\install_codex_backup_task.ps1 -StartTime "06:00" -EveryHours 3
```

## Catatan Keamanan

File `auth.json` tidak dibackup secara default karena bisa berisi kredensial akun.

Kalau benar-benar ingin memasukkan `auth.json`, jalankan:

```powershell
powershell -ExecutionPolicy Bypass -File .\Scripts\backup_codex_data.ps1 -IncludeAuth
```

Gunakan opsi itu hanya untuk backup pribadi yang aman.

## Restore Darurat

Untuk restore, tutup Codex dulu, lalu salin isi folder `snapshot` dari backup ke:

```text
C:\Users\M Fauzan Lubada\.codex
```

Jangan restore `auth.json` dari backup lama kecuali yakin ingin memakai kredensial lama.
