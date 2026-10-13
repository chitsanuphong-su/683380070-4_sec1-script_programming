from unittest.mock import MagicMock
import pytest

from src.email_sender import EmailSender
from src.sms_gateway import SMSGateway


@pytest.fixture
def mock_sender():
    sender = MagicMock(spec=EmailSender)
    sender.send_email.return_value = True
    return sender


def test_sms_gateway_type_error():
    with pytest.raises(TypeError):
        SMSGateway("not an email sender")


def test_sms_gateway_valid_carrier(mock_sender):
    gateway = SMSGateway(mock_sender)
    result = gateway.send_sms("123-456-7890", "Hello there!", carrier_name="att")
    assert result is True
    mock_sender.send_email.assert_called_once_with(
        recipient_email="1234567890@txt.att.net",
        subject="",
        body="Hello there!",
    )


def test_sms_gateway_full_email_address(mock_sender):
    gateway = SMSGateway(mock_sender)
    result = gateway.send_sms("1234567890@txt.att.net", "Hello there!", carrier_name=None)
    assert result is True
    mock_sender.send_email.assert_called_once_with(
        recipient_email="1234567890@txt.att.net",
        subject="",
        body="Hello there!",
    )


def test_sms_gateway_unknown_carrier(mock_sender):
    gateway = SMSGateway(mock_sender)
    result = gateway.send_sms("1234567890", "Hello there!", carrier_name="unknown_thai_carrier")
    assert result is False
    mock_sender.send_email.assert_not_called()


def test_sms_gateway_empty_phone(mock_sender):
    gateway = SMSGateway(mock_sender)
    assert gateway.send_sms("", "Hello") is False


def test_sms_gateway_empty_message(mock_sender):
    gateway = SMSGateway(mock_sender)
    assert gateway.send_sms("1234567890", "", carrier_name="att") is False
