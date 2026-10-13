import pytest
from src.email_tasks import EmailTasks
from src.sms_tasks import SMSTasks

@pytest.fixture
def mock_email_tasks():
    return EmailTasks(
        smtp_server="smtp.example.com",
        smtp_port=587,
        imap_server="imap.example.com",
        sender_email="sender@example.com",
        sender_password="secretpassword",
        dry_run=True
    )

def test_sms_initialization_error():
    with pytest.raises(TypeError, match="requires an instance of EmailTasks"):
        SMSTasks("not_an_email_tasks_instance")

def test_send_sms_valid_carrier(mock_email_tasks):
    sms_tasks = SMSTasks(mock_email_tasks)
    res = sms_tasks.send_sms(
        phone_numbers=["1234567890"],
        message="Test alert",
        carrier_name="att"
    )
    assert res is True

def test_send_sms_unsupported_carrier(mock_email_tasks):
    sms_tasks = SMSTasks(mock_email_tasks)
    res = sms_tasks.send_sms(
        phone_numbers=["1234567890"],
        message="Test alert",
        carrier_name="nonexistent_carrier"
    )
    assert res is False

def test_send_sms_multiple_recipients(mock_email_tasks):
    sms_tasks = SMSTasks(mock_email_tasks)
    res = sms_tasks.send_sms(
        phone_numbers=["1234567890", "0987654321"],
        message="Team alert",
        carrier_name="verizon"
    )
    assert res is True

def test_send_sms_direct_gateway_address(mock_email_tasks):
    sms_tasks = SMSTasks(mock_email_tasks)
    res = sms_tasks.send_sms(
        phone_numbers=["5551234567@tmomail.net"],
        message="Direct gateway SMS"
    )
    assert res is True
