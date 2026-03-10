"""
mailer.py — Dashboard Agro
Kirim email via Gmail SMTP.
Email pengirim: beetcenterindonesia@gmail.com
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
#  KONFIGURASI EMAIL — EDIT BAGIAN INI
# ══════════════════════════════════════════════════════════════════

SMTP_HOST     = 'smtp.gmail.com'
SMTP_PORT     = 587

# Email pengirim
SMTP_USER     = os.environ.get('SMTP_USER',     'beetcenterindonesia@gmail.com')
SMTP_FROM     = 'Dashboard Agro <beetcenterindonesia@gmail.com>'

# ⚠️  PENTING: Isi dengan Gmail App Password (bukan password biasa!)
# Cara mendapatkan App Password:
#   1. Buka https://myaccount.google.com/security
#   2. Pastikan "2-Step Verification" AKTIF
#   3. Buka https://myaccount.google.com/apppasswords
#   4. Pilih "Mail" & "Other (Custom name)" → tulis "Dashboard Agro"
#   5. Klik Generate → salin 16 karakter yang muncul (tanpa spasi)
#   6. Tempel di sini:
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'ajmg utkd pfxp linb')   # ← isi di sini atau set env var

# ══════════════════════════════════════════════════════════════════

DEV_MODE = not bool(SMTP_PASSWORD)


def _check_config():
    if DEV_MODE:
        print("\n" + "⚠️ " * 20)
        print("  [MAILER] SMTP_PASSWORD belum diisi!")
        print("  Email TIDAK akan terkirim — mode DEV aktif.")
        print("  → Edit mailer.py, isi SMTP_PASSWORD dengan Gmail App Password")
        print("  → Atau set environment variable: export SMTP_PASSWORD='xxxx xxxx xxxx xxxx'")
        print("⚠️ " * 20 + "\n")


def send_reset_password(to_email: str, to_name: str, new_password: str) -> bool:
    """
    Kirim email reset password ke pengguna.
    Return True jika berhasil (atau dev mode), False jika gagal kirim.
    """
    subject = "🔑 Reset Password — Dashboard Agro"
    now_str = datetime.now().strftime('%d %B %Y, %H:%M WIB')

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f0f7f0;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f7f0;padding:40px 16px;">
  <tr><td align="center">
    <table width="520" cellpadding="0" cellspacing="0" style="max-width:520px;width:100%;
      background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.1);">

      <!-- Header -->
      <tr>
        <td style="background:linear-gradient(135deg,#1B4332 0%,#2D6A4F 50%,#52B788 100%);
                   padding:36px;text-align:center;">
          <div style="font-size:40px;line-height:1;margin-bottom:12px;">🌱</div>
          <div style="color:#fff;font-size:24px;font-weight:700;letter-spacing:-0.5px;margin-bottom:4px;">
            Dashboard Agro
          </div>
          <div style="color:rgba(255,255,255,.55);font-size:11px;letter-spacing:2px;text-transform:uppercase;">
            Platform Distribusi Pertanian
          </div>
        </td>
      </tr>

      <!-- Body -->
      <tr>
        <td style="padding:36px 36px 24px;">

          <h2 style="margin:0 0 6px;font-size:20px;color:#1A2E1F;font-weight:700;">
            Permintaan Reset Password
          </h2>
          <p style="margin:0 0 28px;font-size:14px;color:#6B8F71;line-height:1.7;">
            Halo <strong style="color:#1A2E1F;">{to_name}</strong>,<br>
            Kami menerima permintaan reset password untuk akun Anda.
            Berikut adalah <strong>password sementara</strong> yang dapat Anda gunakan untuk masuk:
          </p>

          <!-- Password Box -->
          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
            <tr>
              <td style="background:linear-gradient(135deg,#F0FBF5,#D8F3DC);
                         border:2px dashed #52B788;border-radius:14px;
                         padding:24px;text-align:center;">
                <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                            letter-spacing:2px;color:#2D6A4F;margin-bottom:10px;">
                  🔑 Password Sementara
                </div>
                <div style="font-family:'Courier New',Courier,monospace;
                            font-size:30px;font-weight:700;
                            color:#1B4332;letter-spacing:6px;
                            padding:8px 0;">
                  {new_password}
                </div>
              </td>
            </tr>
          </table>

          <!-- Steps -->
          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
            <tr>
              <td style="background:#F8F4EF;border-radius:10px;padding:18px 20px;">
                <div style="font-size:13px;font-weight:700;color:#8B7355;margin-bottom:10px;">
                  📋 Langkah Selanjutnya:
                </div>
                <table cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="padding:4px 0;font-size:13px;color:#5C4A2A;">
                      <span style="display:inline-block;width:22px;height:22px;border-radius:50%;
                        background:#E9C46A;color:#5C4A2A;font-weight:700;font-size:11px;
                        text-align:center;line-height:22px;margin-right:8px;">1</span>
                      Login dengan password sementara di atas
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:4px 0;font-size:13px;color:#5C4A2A;">
                      <span style="display:inline-block;width:22px;height:22px;border-radius:50%;
                        background:#E9C46A;color:#5C4A2A;font-weight:700;font-size:11px;
                        text-align:center;line-height:22px;margin-right:8px;">2</span>
                      Buka menu <strong>Profil</strong> &rarr; <strong>Ganti Password</strong>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:4px 0;font-size:13px;color:#5C4A2A;">
                      <span style="display:inline-block;width:22px;height:22px;border-radius:50%;
                        background:#E9C46A;color:#5C4A2A;font-weight:700;font-size:11px;
                        text-align:center;line-height:22px;margin-right:8px;">3</span>
                      Buat password baru yang kuat dan mudah diingat
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>

          <!-- Warning -->
          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:8px;">
            <tr>
              <td style="background:#FFF7ED;border-left:4px solid #F97316;
                         border-radius:0 8px 8px 0;padding:14px 16px;">
                <div style="font-size:12px;font-weight:700;color:#9A3412;margin-bottom:5px;">
                  ⚠️ Peringatan Keamanan
                </div>
                <div style="font-size:12px;color:#7C2D12;line-height:1.7;">
                  • Jangan bagikan password ini kepada siapapun<br>
                  • Jika Anda tidak merasa meminta reset password, segera hubungi admin<br>
                  • Password ini hanya berlaku untuk satu kali masuk
                </div>
              </td>
            </tr>
          </table>

        </td>
      </tr>

      <!-- Info bar -->
      <tr>
        <td style="background:#F0FBF5;padding:16px 36px;border-top:1px solid #D8F3DC;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="font-size:12px;color:#6B8F71;">
                📧 Dikirim ke: <strong style="color:#1A2E1F;">{to_email}</strong>
              </td>
              <td style="font-size:12px;color:#6B8F71;text-align:right;">
                🕐 {now_str}
              </td>
            </tr>
          </table>
        </td>
      </tr>

      <!-- Footer -->
      <tr>
        <td style="padding:18px 36px 24px;text-align:center;">
          <p style="font-size:11px;color:#B0BEC5;margin:0;line-height:1.7;">
            Email ini dikirim secara otomatis oleh sistem Dashboard Agro.<br>
            Mohon jangan membalas email ini.<br>
            <span style="color:#52B788;">beetcenterindonesia@gmail.com</span>
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""

    text_body = f"""Reset Password — Dashboard Agro
{'='*40}

Halo {to_name},

Password sementara Anda:

    {new_password}

Langkah selanjutnya:
1. Login dengan password sementara di atas
2. Buka menu Profil → Ganti Password
3. Buat password baru yang kuat

Dikirim ke : {to_email}
Waktu      : {now_str}

PERINGATAN: Jangan bagikan password ini kepada siapapun.
Jika Anda tidak merasa meminta reset, hubungi admin segera.

— Tim Dashboard Agro
"""

    # ── Dev Mode ──────────────────────────────────────────────────────────────
    if DEV_MODE:
        _check_config()
        print("╔" + "═"*54 + "╗")
        print("║  📧  [DEV] Simulasi Email Reset Password          ║")
        print("╠" + "═"*54 + "╣")
        print(f"║  To      : {to_name:<41}║")
        print(f"║  Email   : {to_email:<41}║")
        print(f"║  Password: {new_password:<41}║")
        print(f"║  Waktu   : {now_str:<41}║")
        print("╚" + "═"*54 + "╝\n")
        return True   # Dev mode selalu anggap sukses

    # ── Production: kirim via Gmail SMTP ─────────────────────────────────────
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = SMTP_FROM
        msg['To']      = f"{to_name} <{to_email}>"
        msg['Reply-To'] = SMTP_FROM

        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html',  'utf-8'))

        print(f"[mailer] Menghubungi {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())

        print(f"[mailer] ✅ Email terkirim ke {to_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[mailer] ❌ GAGAL: Username/App Password salah.")
        print("         → Pastikan menggunakan App Password, bukan password Gmail biasa.")
        print("         → Buka: https://myaccount.google.com/apppasswords")
        return False
    except smtplib.SMTPException as e:
        print(f"[mailer] ❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"[mailer] ❌ Error: {e}")
        return False
