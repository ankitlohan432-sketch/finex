import logging
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

# ── Gmail SMTP config ─────────────────────────────────────────────────────────
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587
SMTP_USER     = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
FROM_NAME     = "Finex"

MAX_EMAILS_PER_USER = 5

class MailService:
    def __init__(self):
        self.user_log = defaultdict(list)

    def _check_rate_limit(self, to_email: str):
        now      = datetime.now()
        hour_ago = now - timedelta(hours=1)
        self.user_log[to_email] = [t for t in self.user_log.get(to_email, []) if t > hour_ago]
        if len(self.user_log.get(to_email, [])) >= MAX_EMAILS_PER_USER:
            return False, "Too many emails sent to this address"
        return True, "OK"

    def _send(self, to_email: str, to_name: str, subject: str, html: str):
        if not SMTP_USER or not SMTP_PASSWORD:
            logger.error("SMTP_USER or SMTP_PASSWORD not set in environment variables.")
            return False

        allowed, reason = self._check_rate_limit(to_email)
        if not allowed:
            logger.error(f"Rate limit: {reason} for {to_email}")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = f"{FROM_NAME} <{SMTP_USER}>"
            msg["To"]      = f"{to_name} <{to_email}>"
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, to_email, msg.as_string())

            logger.info(f"Email sent to {to_email}: {subject}")
            self.user_log[to_email].append(datetime.now())
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Gmail SMTP auth failed — check SMTP_USER and SMTP_PASSWORD")
            return False
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    # ── OTP Verification Email ────────────────────────────────────────────────

    async def send_otp_email(self, to_email: str, full_name: str, otp: str):
        html = f"""
        <div style="font-family:sans-serif;max-width:520px;margin:0 auto;background:#0f172a;color:#fff;border-radius:16px;overflow:hidden">
          <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);padding:32px 32px 20px">
            <h1 style="font-size:28px;margin:0 0 4px">Fin<span style="color:#38bdf8">ex</span></h1>
            <p style="color:rgba(255,255,255,0.5);margin:0;font-size:13px">Email Verification</p>
          </div>
          <div style="padding:28px 32px">
            <h2 style="font-size:20px;margin:0 0 12px">Hi {full_name} 👋</h2>
            <p style="color:rgba(255,255,255,0.7);line-height:1.7;margin-bottom:24px">
              Use the code below to verify your Finex account.
              It expires in <strong>10 minutes</strong>.
            </p>
            <div style="background:rgba(56,189,248,0.1);border:2px dashed #38bdf8;border-radius:14px;padding:28px;text-align:center;margin-bottom:24px">
              <div style="font-size:42px;font-weight:900;letter-spacing:12px;color:#38bdf8;font-family:monospace">{otp}</div>
              <div style="color:rgba(255,255,255,0.4);font-size:12px;margin-top:8px">One-Time Password · Valid for 10 minutes</div>
            </div>
            <p style="color:rgba(255,255,255,0.4);font-size:12px;margin:0">
              If you didn't create a Finex account, ignore this email. Never share this code.
            </p>
          </div>
        </div>
        """
        self._send(to_email, full_name, "Your Finex Verification Code", html)

    # ── Welcome Email ─────────────────────────────────────────────────────────

    async def send_welcome_email(self, to_email: str, full_name: str):
        html = f"""
        <div style="font-family:sans-serif;max-width:520px;margin:0 auto;background:#0f172a;color:#fff;border-radius:16px;overflow:hidden">
          <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);padding:32px 32px 20px">
            <h1 style="font-size:28px;margin:0 0 4px">Fin<span style="color:#38bdf8">ex</span></h1>
            <p style="color:rgba(255,255,255,0.5);margin:0;font-size:13px">Your Financial Platform</p>
          </div>
          <div style="padding:28px 32px">
            <h2 style="font-size:20px;margin:0 0 12px">Welcome, {full_name}! 🎉</h2>
            <p style="color:rgba(255,255,255,0.7);line-height:1.7;margin-bottom:24px">
              Your Finex account is ready. Access real-time markets,
              manage your portfolio, and use our AI financial tools.
            </p>
            <a href="https://finex-nu.vercel.app/login"
               style="display:inline-block;padding:13px 28px;background:#38bdf8;color:#07111e;border-radius:8px;text-decoration:none;font-weight:700;font-size:14px">
              Sign In to Dashboard →
            </a>
            <hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:28px 0">
            <p style="color:rgba(255,255,255,0.35);font-size:12px;margin:0">
              © 2026 Finex. If you didn't sign up, ignore this email.
            </p>
          </div>
        </div>
        """
        self._send(to_email, full_name, "Welcome to Finex!", html)

    # ── Login Alert Email ─────────────────────────────────────────────────────

    async def send_login_alert(self, to_email: str, full_name: str, ip: str = "Unknown"):
        html = f"""
        <div style="font-family:sans-serif;max-width:520px;margin:0 auto;background:#0f172a;color:#fff;border-radius:16px;overflow:hidden">
          <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);padding:32px 32px 20px">
            <h1 style="font-size:28px;margin:0 0 4px">Fin<span style="color:#38bdf8">ex</span></h1>
          </div>
          <div style="padding:28px 32px">
            <h2 style="font-size:18px;margin:0 0 12px">New Login Detected 🔐</h2>
            <p style="color:rgba(255,255,255,0.7)">Hi {full_name}, a new login was detected.</p>
            <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:16px;margin:16px 0">
              <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:4px">IP Address</div>
              <div style="font-family:monospace;color:#38bdf8">{ip}</div>
            </div>
            <p style="color:rgba(255,255,255,0.5);font-size:13px">
              If this wasn't you, change your password immediately.
            </p>
          </div>
        </div>
        """
        self._send(to_email, full_name, "New Login to Your Finex Account", html)

    # ── Password Reset Email ──────────────────────────────────────────────────

    async def send_password_reset_email(self, to_email: str, full_name: str, otp: str):
        html = f"""
        <div style="font-family:sans-serif;max-width:520px;margin:0 auto;background:#0f172a;color:#fff;border-radius:16px;overflow:hidden">
          <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);padding:32px 32px 20px">
            <h1 style="font-size:28px;margin:0 0 4px">Fin<span style="color:#38bdf8">ex</span></h1>
            <p style="color:rgba(255,255,255,0.5);margin:0;font-size:13px">Password Reset</p>
          </div>
          <div style="padding:28px 32px">
            <h2 style="font-size:20px;margin:0 0 12px">Hi {full_name},</h2>
            <p style="color:rgba(255,255,255,0.7);line-height:1.7;margin-bottom:24px">
              Your password reset code is below. Expires in <strong>10 minutes</strong>.
            </p>
            <div style="background:rgba(56,189,248,0.1);border:2px dashed #38bdf8;border-radius:14px;padding:28px;text-align:center;margin-bottom:24px">
              <div style="font-size:42px;font-weight:900;letter-spacing:12px;color:#38bdf8;font-family:monospace">{otp}</div>
              <div style="color:rgba(255,255,255,0.4);font-size:12px;margin-top:8px">
                Password Reset Code · Valid for 10 minutes
              </div>
            </div>
            <p style="color:rgba(255,255,255,0.4);font-size:12px;margin:0">
              If you didn't request this, ignore this email.
            </p>
          </div>
        </div>
        """
        self._send(to_email, full_name, "FINEX — Password Reset Code", html)


# Module-level singleton
mail_service = MailService()
