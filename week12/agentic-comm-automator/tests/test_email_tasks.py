import pytest
import os
from unittest.mock import MagicMock, patch
from src.email_tasks import EmailTasks

@pytest.fixture
def email_tasks():
    return EmailTasks(
        smtp_server="smtp.example.com",
        smtp_port=587,
        imap_server="imap.example.com",
        sender_email="sender@example.com",
        sender_password="secretpassword",
        dry_run=True
    )

def test_dry_run_send_email_plaintext(email_tasks):
    recipients = {"to": ["user@example.com"], "cc": ["cc@example.com"], "bcc": ["bcc@example.com"]}
    result = email_tasks.send_email(
        recipients=recipients,
        subject="Test Subject",
        body="Test Body"
    )
    assert result is True

def test_dry_run_send_email_missing_attachment(email_tasks):
    recipients = {"to": ["user@example.com"]}
    result = email_tasks.send_email(
        recipients=recipients,
        subject="Test Subject",
        body="Test Body",
        attachments=["non_existent_file.pdf"]
    )
    assert result is False

def test_dry_run_send_email_with_valid_attachment(email_tasks, tmp_path):
    sample_file = tmp_path / "test.txt"
    sample_file.write_text("sample content")

    recipients = {"to": ["user@example.com"]}
    result = email_tasks.send_email(
        recipients=recipients,
        subject="Test With Attachment",
        body="Body",
        attachments=[str(sample_file)]
    )
    assert result is True

def test_send_email_no_recipients(email_tasks):
    result = email_tasks.send_email(
        recipients={"to": [], "cc": [], "bcc": []},
        subject="Subject",
        body="Body"
    )
    assert result is False

def test_dry_run_search_and_fetch_emails(email_tasks, tmp_path):
    uids = email_tasks.search_emails(mailbox="INBOX", criteria="UNSEEN")
    assert len(uids) == 1
    assert uids[0] == b"101"

    download_dir = tmp_path / "downloads"
    email_data = email_tasks.fetch_email_content(
        uid=uids[0],
        mark_as_read=True,
        download_attachments_dir=str(download_dir)
    )
    assert email_data is not None
    assert email_data["uid"] == "101"
    assert email_data["has_attachments"] is True
    assert len(email_data["attachments_meta"]) == 1
    assert os.path.exists(email_data["attachments_meta"][0]["filepath"])

def test_decode_header_part(email_tasks):
    decoded = email_tasks._decode_header_part("Simple Subject")
    assert decoded == "Simple Subject"
    assert email_tasks._decode_header_part(None) == ""
