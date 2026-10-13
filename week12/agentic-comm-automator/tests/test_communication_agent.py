import pytest
import os
import json
from src.communication_agent import CommunicationAgent
from src.config_parser import ConfigParser

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("SENDER_EMAIL", "test_sender@example.com")
    monkeypatch.setenv("SENDER_APP_PASSWORD", "test_pass")
    monkeypatch.setenv("SMTP_SERVER", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("IMAP_SERVER", "imap.example.com")
    monkeypatch.setenv("TEST_RECIPIENT_EMAIL", "test_recipient@example.com")
    monkeypatch.setenv("TEST_SMS_PHONE_NUMBER", "1234567890")
    monkeypatch.setenv("TEST_SMS_CARRIER", "att")

def test_communication_agent_initialization(tmp_path):
    config = {"tasks": []}
    agent = CommunicationAgent(config=config, base_dir=str(tmp_path), dry_run=True)
    assert agent.dry_run is True
    assert agent.task_stats["total_tasks"] == 0

def test_full_pipeline_dry_run():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(base_dir, "configs", "comm_pipeline_config.json")

    parser = ConfigParser(config_path)
    config = parser.load_config()

    agent = CommunicationAgent(config=config, base_dir=base_dir, dry_run=True)
    report_file = agent.run()

    assert os.path.exists(report_file)

    with open(report_file, "r", encoding="utf-8") as f:
        report = json.load(f)

    assert "summary" in report
    assert report["summary"]["final_status"] == "SUCCESS"
    assert report["summary"]["stats"]["total_tasks"] == 4
    assert report["summary"]["stats"]["successful_tasks"] == 4
    assert report["summary"]["stats"]["failed_tasks"] == 0

    # Verify context chaining occurred
    assert "simulated_email_sent" in agent.context
    assert "processed_inbox_results" in agent.context
    assert agent.context["processed_inbox_results"]["processed_emails_count"] == 1
