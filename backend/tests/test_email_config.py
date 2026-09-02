import app.notifications.email_service as email_service
from app.notifications.email_service import normalize_gmail_password


def test_normalize_gmail_password_removes_spaces_and_keeps_16char_value():
    assert normalize_gmail_password("exyr danb nqse tmxv") == "exyrdanbnqsetmxv"
    assert normalize_gmail_password("  exyrdanbnqsetmxv  ") == "exyrdanbnqsetmxv"


def test_send_verification_email_logs_smtp_progress(monkeypatch, capsys):
    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.logged_in = False
            self.closed = False

        def starttls(self):
            return None

        def login(self, username, password):
            self.logged_in = True
            assert username == "sender@example.com"
            assert password == "appsecret"

        def send_message(self, msg):
            return {"status": "queued"}

        def quit(self):
            self.closed = True

    monkeypatch.setattr(email_service, "EMAIL", "sender@example.com")
    monkeypatch.setattr(email_service, "PASSWORD", "appsecret")
    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    result = email_service.send_verification_email("user@example.com", "token-123")

    captured = capsys.readouterr().out
    assert result is True
    assert "SMTP TLS established" in captured
    assert "SMTP authentication successful" in captured
    assert "SMTP send response" in captured
    assert "Verification email accepted" in captured
