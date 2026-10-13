import re
from typing import Optional

try:
    from .email_sender import EmailSender
    from .utils import setup_logging
except ImportError:
    from email_sender import EmailSender
    from utils import setup_logging

logger = setup_logging(__name__)


class SMSGateway:
    """
    Provides an interface to send SMS via email-to-SMS carrier gateways.
    Relies on EmailSender for actual email transmission.
    """

    def __init__(self, email_sender_instance: EmailSender):
        if not isinstance(email_sender_instance, EmailSender):
            raise TypeError("SMSGateway requires an instance of EmailSender.")
        self.email_sender = email_sender_instance

        # Common US carrier email-to-SMS gateways (as described in the assignment)
        self.carrier_gateways = {
            "att": "@txt.att.net",
            "verizon": "@vtext.com",
            "tmobile": "@tmomail.net",
            "sprint": "@messaging.sprintpcs.com",
            "boost": "@sms.boostmobile.com",
            "cricket": "@mms.cricketwireless.net",
            "us_cellular": "@email.uscc.net",
        }
        logger.info("SMSGateway initialized.")

    def send_sms(
        self,
        phone_number: str,
        message: str,
        carrier_name: Optional[str] = None,
    ) -> bool:
        """
        Sends an SMS message via email-to-SMS gateway.
        :param phone_number: Recipient phone number (e.g., '1234567890') or full gateway address.
        :param message: The text message content.
        :param carrier_name: Optional specific carrier (e.g., 'att', 'verizon').
        :return: True if message sent (via email), False otherwise.
        """
        if not phone_number or not str(phone_number).strip():
            logger.error("Phone number cannot be empty.")
            return False

        if not message or not str(message).strip():
            logger.error("SMS message content cannot be empty.")
            return False

        cleaned_phone = str(phone_number).strip()
        sms_gateway_address = None

        if carrier_name and carrier_name.strip().lower() in self.carrier_gateways:
            # Strip non-digits from phone number when using carrier lookup
            digits_only = re.sub(r"\D", "", cleaned_phone)
            if not digits_only:
                logger.error(f"Invalid phone number '{phone_number}': no digits found.")
                return False
            domain = self.carrier_gateways[carrier_name.strip().lower()]
            sms_gateway_address = f"{digits_only}{domain}"
        elif "@" in cleaned_phone and "." in cleaned_phone:
            # Already a full email gateway address
            sms_gateway_address = cleaned_phone
        else:
            logger.warning(
                f"No supported carrier provided ('{carrier_name}') and phone number is not a gateway address. "
                f"Available carriers: {', '.join(sorted(self.carrier_gateways.keys()))}. Cannot send SMS."
            )
            return False

        if sms_gateway_address:
            subject = ""  # SMS emails usually omit the subject line
            logger.info(
                f"Attempting to send SMS to {phone_number} via gateway: {sms_gateway_address}"
            )
            return self.email_sender.send_email(
                recipient_email=sms_gateway_address,
                subject=subject,
                body=message,
            )
        else:
            logger.error("Could not determine SMS gateway address.")
            return False
