import pytest
import os
import json
from src.config_parser import ConfigParser

def test_load_valid_config(tmp_path):
    config_content = {
        "tasks": [
            {
                "name": "Test Email",
                "type": "send_email",
                "parameters": {
                    "recipients": {"to": ["test@example.com"]},
                    "subject_template": "Subject",
                    "body_template": "Body"
                }
            }
        ]
    }
    cfg_file = tmp_path / "valid_config.json"
    cfg_file.write_text(json.dumps(config_content), encoding="utf-8")

    parser = ConfigParser(str(cfg_file))
    loaded = parser.load_config()
    assert "tasks" in loaded
    assert len(loaded["tasks"]) == 1

def test_missing_config_file():
    parser = ConfigParser("non_existent_file.json")
    with pytest.raises(FileNotFoundError):
        parser.load_config()

def test_malformed_json(tmp_path):
    cfg_file = tmp_path / "bad.json"
    cfg_file.write_text("{tasks: [bad json", encoding="utf-8")
    parser = ConfigParser(str(cfg_file))
    with pytest.raises(ValueError, match="Invalid JSON format"):
        parser.load_config()

def test_missing_tasks_field(tmp_path):
    cfg_file = tmp_path / "no_tasks.json"
    cfg_file.write_text(json.dumps({"version": "1.0"}), encoding="utf-8")
    parser = ConfigParser(str(cfg_file))
    with pytest.raises(ValueError, match="Missing required field in config: 'tasks'"):
        parser.load_config()

def test_invalid_task_type(tmp_path):
    cfg_file = tmp_path / "invalid_type.json"
    content = {
        "tasks": [
            {
                "name": "Invalid Task",
                "type": "unsupported_task_type",
                "parameters": {}
            }
        ]
    }
    cfg_file.write_text(json.dumps(content), encoding="utf-8")
    parser = ConfigParser(str(cfg_file))
    with pytest.raises(ValueError, match="unsupported task type"):
        parser.load_config()

def test_invalid_send_email_recipients(tmp_path):
    cfg_file = tmp_path / "invalid_email.json"
    content = {
        "tasks": [
            {
                "name": "Test Email",
                "type": "send_email",
                "parameters": {
                    "recipients": {"to": "not-a-list@example.com"},
                    "subject_template": "Subject",
                    "body_template": "Body"
                }
            }
        ]
    }
    cfg_file.write_text(json.dumps(content), encoding="utf-8")
    parser = ConfigParser(str(cfg_file))
    with pytest.raises(ValueError, match="'recipients.to' must be a non-empty list"):
        parser.load_config()

def test_invalid_send_sms_params(tmp_path):
    cfg_file = tmp_path / "invalid_sms.json"
    content = {
        "tasks": [
            {
                "name": "Test SMS",
                "type": "send_sms",
                "parameters": {
                    "phone_numbers": [],
                    "message_template": "Hello"
                }
            }
        ]
    }
    cfg_file.write_text(json.dumps(content), encoding="utf-8")
    parser = ConfigParser(str(cfg_file))
    with pytest.raises(ValueError, match="non-empty 'phone_numbers' list"):
        parser.load_config()

def test_invalid_process_inbox_rules(tmp_path):
    cfg_file = tmp_path / "invalid_inbox.json"
    content = {
        "tasks": [
            {
                "name": "Process Inbox",
                "type": "process_inbox",
                "parameters": {
                    "search_criteria": {"status": "UNSEEN"},
                    "rules": ["not-a-dict"]
                }
            }
        ]
    }
    cfg_file.write_text(json.dumps(content), encoding="utf-8")
    parser = ConfigParser(str(cfg_file))
    with pytest.raises(ValueError, match="must contain 'if' and 'then' blocks"):
        parser.load_config()
