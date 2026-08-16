from app.notifications.email_service import normalize_gmail_password


def test_normalize_gmail_password_removes_spaces_and_keeps_16char_value():
    assert normalize_gmail_password("exyr danb nqse tmxv") == "exyrdanbnqsetmxv"
    assert normalize_gmail_password("  exyrdanbnqsetmxv  ") == "exyrdanbnqsetmxv"
