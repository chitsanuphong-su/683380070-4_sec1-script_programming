import email
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import os
from unittest.mock import MagicMock, patch
import pytest

from src.email_receiver import EmailReceiver


def test_email_receiver_init():
    receiver = EmailReceiver("imap.example.com", "user@example.com", "secret")
    assert receiver.imap_server == "imap.example.com"
    assert receiver.sender_email == "user@example.com"
    assert receiver.dry_run is False


def test_email_receiver_dry_run_simulation(tmp_path):
    receiver = EmailReceiver("imap.example.com", "user@example.com", "secret", dry_run=True)
    attachments_dir = tmp_path / "downloads"

    receiver._dry_run_messages[b"99"] = {
        "from": "user@example.com",
        "subject": "Demo Report",
        "body": "Hello world from simulated IMAP email body",
        "attachment_filename": "report.pdf",
        "attachment_data": b"%PDF-1.4 sample",
        "seen": False,
    }

    # Search
    uids = receiver.search_emails(
        criteria="UNSEEN",
        from_sender="user@example.com",
        subject_contains="Demo Report",
    )
    assert uids == [b"99"]

    # Fetch
    details = receiver.fetch_email_content(
        uid=b"99",
        mark_as_read=True,
        download_attachments_dir=str(attachments_dir),
    )
    assert details is not None
    assert details["uid"] == "99"
    assert details["sender"] == "user@example.com"
    assert details["subject"] == "Demo Report"
    assert "Hello world" in details["body_snippet"]
    assert len(details["attachments_downloaded"]) == 1
    assert os.path.isfile(details["attachments_downloaded"][0])


@patch("imaplib.IMAP4_SSL")
def test_email_receiver_live_mock(mock_imap_class, tmp_path):
    mock_imap = MagicMock()
    mock_imap_class.return_value = mock_imap

    # Build genuine RFC822 raw message
    msg = MIMEMultipart()
    msg["From"] = "Tester <tester@example.com>"
    msg["Subject"] = "Test IMAP Subject"
    msg.attach(MIMEText("Plain text body content", "plain"))
    part = MIMEApplication(b"dummy pdf bytes", Name="file.pdf")
    part["Content-Disposition"] = 'attachment; filename="file.pdf"'
    msg.attach(part)
    raw_bytes = msg.as_bytes()

    mock_imap.uid.side_effect = [
        ("OK", [b"1 2 3"]),  # search
        ("OK", [(b"1 (RFC822 {100})", raw_bytes)]),  # fetch
        ("OK", [b"Store completed"]),  # store
    ]

    receiver = EmailReceiver("imap.example.com", "user@example.com", "secret", dry_run=False)

    # Search test
    uids = receiver.search_emails(criteria="UNSEEN", from_sender="tester@example.com")
    assert uids == [b"1", b"2", b"3"]

    # Fetch test
    download_dir = tmp_path / "test_down"
    details = receiver.fetch_email_content(b"1", mark_as_read=True, download_attachments_dir=str(download_dir))

    assert details is not None
    assert details["uid"] == "1"
    assert "tester@example.com" in details["sender"]
    assert details["subject"] == "Test IMAP Subject"
    assert "Plain text body" in details["body_snippet"]
    assert len(details["attachments_downloaded"]) == 1


def test_sanitize_filename():
    receiver = EmailReceiver("imap.example.com", "user@example.com", "secret", dry_run=True)
    assert receiver._sanitize_filename("../../etc/passwd") == "passwd"
    assert receiver._sanitize_filename("test:file?.txt") == "test_file_.txt"
