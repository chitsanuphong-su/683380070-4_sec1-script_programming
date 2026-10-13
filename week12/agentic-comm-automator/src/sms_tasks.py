from .utils import setup_logging
from .email_tasks import EmailTasks
from .template_renderer import TemplateRenderer

logger = setup_logging(__name__)

class SMSTasks:
    """
    Provides an interface to send SMS messages via carrier email-to-SMS gateways.
    Relies on EmailTasks for message transmission.
    """

    def __init__(self, email_tasks_instance):
        if not isinstance(email_tasks_instance, EmailTasks):
            raise TypeError("SMSTasks requires an instance of EmailTasks.")
        self.email_tasks = email_tasks_instance
        self.template_renderer = TemplateRenderer()

        # Common carrier email-to-SMS gateways
        self.carrier_gateways = {
            "att": "@txt.att.net",
            "verizon": "@vtext.com",
            "tmobile": "@tmomail.net",
            "sprint": "@messaging.sprintpcs.com",
            "boost": "@sms.boostmobile.com",
            "cricket": "@mms.cricketwireless.net",
            "us_cellular": "@email.uscc.net",
        }
        logger.info("SMSTasks initialized.")

    def send_sms(self, phone_numbers, message, carrier_name=None):
        """
        Sends SMS messages via email-to-SMS gateway for multiple recipients.
        :param phone_numbers: List of recipient phone numbers (e.g., ['1234567890']).
        :param message: The text message content.
        :param carrier_name: Optional, specific carrier (e.g., 'att', 'verizon').
        :return: True if all valid recipients were accepted by the mail gateway, False otherwise.
        """
        success_count = 0
        total_attempts = 0

        for phone_number in phone_numbers:
            total_attempts += 1
            sms_gateway_address = None

            if carrier_name and carrier_name.lower() in self.carrier_gateways:
                sms_gateway_address = f"{phone_number}{self.carrier_gateways[carrier_name.lower()]}"
            elif '@' in phone_number and '.' in phone_number:
                # If already formatted as a full gateway address
                sms_gateway_address = phone_number
            else:
                logger.warning(
                    f"No supported carrier provided for '{phone_number}' (carrier: '{carrier_name}') "
                    f"and it is not an email address. Cannot resolve SMS gateway."
                )
                continue

            if sms_gateway_address:
                logger.info(f"Attempting to send SMS to {phone_number} via gateway: {sms_gateway_address}")
                # SMS messages typically omit subject or keep it empty
                if self.email_tasks.send_email(
                    recipients={'to': [sms_gateway_address]},
                    subject="",
                    body=message
                ):
                    success_count += 1
                else:
                    logger.error(f"Failed to transmit SMS email to gateway {sms_gateway_address}.")

        if total_attempts > 0:
            logger.info(f"Attempted {total_attempts} SMS messages: {success_count} succeeded at gateway level.")
            return success_count == total_attempts
        return False
