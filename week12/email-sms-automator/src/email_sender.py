import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

try:
    from .utils import setup_logging
except ImportError:
    from utils import setup_logging

logger = setup_logging(__name__)


class EmailSender:
    """
    Handles sending emails via SMTP.
    Supports live network sending and simulated dry-run mode.
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        dry_run: bool = False,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = int(smtp_port)
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.dry_run = dry_run
        self.server: Optional[smtplib.SMTP] = None
        logger.info(
            f"EmailSender initialized for {sender_email} via {smtp_server}:{smtp_port} "
            f"(dry_run={self.dry_run})."
        )

    def _connect(self) -> bool:
        """Establishes and logs into the SMTP server using TLS."""
        if self.dry_run:
            logger.info("[DRY RUN] Simulating SMTP connection, TLS handshake, and login.")
            return True

        try:
            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            self.server.starttls()
            self.server.login(self.sender_email, self.sender_password)
            logger.info("Successfully connected and logged into SMTP server.")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed. Check email and app password. Error: {e}")
            self.server = None
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP connection failed. Check server address and port. Error: {e}")
            self.server = None
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during SMTP connect/login: {e}")
            self.server = None
            return False

    def _disconnect(self) -> None:
        """Disconnects safely from the SMTP server."""
        if self.dry_run:
            logger.info("[DRY RUN] Simulating SMTP disconnection.")
            self.server = None
            return

        if self.server:
            try:
                self.server.quit()
                logger.info("Disconnected from SMTP server.")
            except Exception as e:
                logger.warning(f"Error during SMTP disconnection: {e}")
            finally:
                self.server = None

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
        is_html: bool = False,
    ) -> bool:
        """
        Sends an email.
        :param recipient_email: The email address of the recipient.
        :param subject: The subject line of the email.
        :param body: The content of the email.
        :param attachment_path: Optional path to a file to attach.
        :param is_html: Set to True if body is HTML, False for plain text.
        :return: True if email sent successfully, False otherwise.
        """
        if not recipient_email or not recipient_email.strip():
            logger.error("Recipient email cannot be empty.")
            return False

        # Validate attachment before starting connection
        part_attachment = None
        if attachment_path:
            if not os.path.isfile(attachment_path):
                logger.error(f"Attachment file not found: {attachment_path}. Aborting send.")
                return False
            try:
                with open(attachment_path, "rb") as f:
                    filename = os.path.basename(attachment_path)
                    part_attachment = MIMEApplication(f.read(), Name=filename)
                    part_attachment["Content-Disposition"] = f'attachment; filename="{filename}"'
                logger.info(f"Attached file: {attachment_path}")
            except Exception as e:
                logger.error(f"Error attaching file {attachment_path}: {e}. Aborting send.")
                return False

        # Construct MIME Message
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        if is_html:
            msg.attach(MIMEText(body, "html", "utf-8"))
        else:
            msg.attach(MIMEText(body, "plain", "utf-8"))

        if part_attachment:
            msg.attach(part_attachment)

        if not self._connect():
            return False

        try:
            if self.dry_run:
                logger.info(
                    f"[DRY RUN] Simulated sending email to {recipient_email} with subject: '{subject}'."
                )
                return True

            self.server.send_message(msg)
            logger.info(f"Email sent successfully to {recipient_email} with subject: '{subject}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}. Error: {e}")
            return False
        finally:
            self._disconnect()
