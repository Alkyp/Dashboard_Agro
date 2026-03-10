# 📧 Panduan Setup Email — Dashboard Agro

Email pengirim sudah dikonfigurasi: **beetcenterindonesia@gmail.com**

Yang perlu Anda lakukan hanya **satu langkah**: mendapatkan Gmail App Password.

---

## 🔑 Cara Mendapatkan Gmail App Password

> **Kenapa perlu App Password?**
> Google tidak mengizinkan login langsung dari aplikasi sejak 2022.
> App Password adalah kode 16 karakter khusus untuk aplikasi tertentu.

### Langkah-langkah:

**1. Aktifkan 2-Step Verification (jika belum)**
- Buka → https://myaccount.google.com/security
- Scroll ke bagian "How you sign in to Google"
- Klik **"2-Step Verification"** → ikuti instruksi

**2. Buka halaman App Passwords**
- Buka → https://myaccount.google.com/apppasswords
- (atau search "App Passwords" di Google Account)

**3. Buat App Password baru**
- Di kolom "App name" ketik: `Dashboard Agro`
- Klik **"Create"**
- Salin **16 karakter** yang muncul (contoh: `abcd efgh ijkl mnop`)

**4. Isi App Password di kode**

Buka file `mailer.py`, cari baris ini:
```python
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')   # ← isi di sini
```

Ubah menjadi (ganti dengan App Password Anda):
```python
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'abcdefghijklmnop')
```
> Tulis tanpa spasi, contoh: `'abcdefghijklmnop'`

---

## ✅ Cara Test

Jalankan test ini di terminal:
```bash
cd dashboard_agro_new
python3 -c "
from mailer import send_reset_password
ok = send_reset_password('test@gmail.com', 'Test User', 'TestPass123')
print('Berhasil!' if ok else 'Gagal!')
"
```

---

## 🌐 Alternatif: Environment Variable (lebih aman)

Jika tidak ingin password ada di kode, set environment variable sebelum jalankan app:

**Windows (Command Prompt):**
```cmd
set SMTP_PASSWORD=abcdefghijklmnop
python app.py
```

**Mac / Linux:**
```bash
export SMTP_PASSWORD="abcdefghijklmnop"
python3 app.py
```

---

## ❗ Troubleshooting

| Error | Solusi |
|---|---|
| `SMTPAuthenticationError` | App Password salah / belum diisi |
| `2-Step Verification not enabled` | Aktifkan dulu di Google Account |
| Email masuk spam | Tambah kontak beetcenterindonesia@gmail.com di penerima |
| `Connection timeout` | Cek koneksi internet / firewall port 587 |
