import os
import smtplib
from unittest.mock import MagicMock, patch
import pytest

from src.email_sender import EmailSender


@pytest.fixture
def dummy_pdf(tmp_path):
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"%PDF-1.4 dummy test content")
    return str(pdf)


def test_email_sender_init():
    sender = EmailSender("smtp.example.com", 587, "user@example.com", "secret")
    assert sender.smtp_server == "smtp.example.com"
    assert sender.smtp_port == 587
    assert sender.sender_email == "user@example.com"
    assert sender.dry_run is False


def test_email_sender_dry_run(dummy_pdf):
    sender = EmailSender("smtp.example.com", 587, "user@example.com", "secret", dry_run=True)
    res = sender.send_email("to@example.com", "Subject", "Body", attachment_path=dummy_pdf)
    assert res is True


def test_email_sender_missing_attachment():
    sender = EmailSender("smtp.example.com", 587, "user@example.com", "secret", dry_run=True)
    res = sender.send_email("to@example.com", "Subject", "Body", attachment_path="non_existent.pdf")
    assert res is False


def test_email_sender_empty_recipient():
    sender = EmailSender("smtp.example.com", 587, "user@example.com", "secret", dry_run=True)
    res = sender.send_email("", "Subject", "Body")
    assert res is False


@patch("smtplib.SMTP")
def test_email_sender_live_mock_send(mock_smtp_class, dummy_pdf):
    mock_smtp_instance = MagicMock()
    mock_smtp_class.return_value = mock_smtp_instance

    sender = EmailSender("smtp.example.com", 587, "user@example.com", "secret", dry_run=False)
    res = sender.send_email(
        "recipient@example.com",
        "Test Subject",
        "Hello body",
        attachment_path=dummy_pdf,
        is_html=False,
    )

    assert res is True
    mock_smtp_class.assert_called_once_with("smtp.example.com", 587, timeout=30)
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("user@example.com", "secret")
    mock_smtp_instance.send_message.assert_called_once()
    mock_smtp_instance.quit.assert_called_once()


@patch("smtplib.SMTP")
def test_email_sender_auth_failure(mock_smtp_class):
    mock_smtp_instance = MagicMock()
    mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
    mock_smtp_class.return_value = mock_smtp_instance

    sender = EmailSender("smtp.example.com", 587, "user@example.com", "secret", dry_run=False)
    res = sender.send_email("to@example.com", "Sub", "Body")
    assert res is False


@patch("smtplib.SMTP")
def test_email_sender_connect_failure(mock_smtp_class):
    mock_smtp_class.side_effect = smtplib.SMTPConnectError(421, "Cannot connect")

    sender = EmailSender("smtp.example.com", 587, "user@example.com", "secret", dry_run=False)
    res = sender.send_email("to@example.com", "Sub", "Body")
    assert res is False
