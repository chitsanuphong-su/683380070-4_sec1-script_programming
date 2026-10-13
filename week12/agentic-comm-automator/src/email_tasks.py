import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import decode_header
import os
import ssl
from pathlib import Path
from .utils import setup_logging, ensure_directory_exists
from .template_renderer import TemplateRenderer

logger = setup_logging(__name__)

class EmailTasks:
    """
    Handles sending and receiving emails via SMTP and IMAP protocols.
    Supports dry-run mode where no actual network calls are executed.
    """

    def __init__(self, smtp_server, smtp_port, imap_server, sender_email, sender_password, dry_run=True):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.dry_run = dry_run
        self._smtp_server = None
        self._imap_mail = None
        self.template_renderer = TemplateRenderer()
        logger.info(f"EmailTasks initialized for {sender_email} (Dry-run: {dry_run}).")

    def _connect_smtp(self):
        """Establishes and logs into the SMTP server."""
        if self.dry_run:
            logger.info("[DRY-RUN] Simulating SMTP connection and authentication.")
            return True
        if self._smtp_server:
            return True
        try:
            context = ssl.create_default_context()
            self._smtp_server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            self._smtp_server.starttls(context=context)
            self._smtp_server.login(self.sender_email, self.sender_password)
            logger.info("Successfully connected and logged into SMTP server.")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed. Check credentials. Error: {e}")
            self._smtp_server = None
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP connection failed. Check host/port. Error: {e}")
            self._smtp_server = None
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during SMTP connect/login: {e}")
            self._smtp_server = None
            return False

    def _disconnect_smtp(self):
        """Disconnects from the SMTP server."""
        if self.dry_run:
            logger.info("[DRY-RUN] Simulating SMTP disconnection.")
            return
        if self._smtp_server:
            try:
                self._smtp_server.quit()
                logger.info("Disconnected from SMTP server.")
            except Exception as e:
                logger.warning(f"Error during SMTP disconnection: {e}")
            finally:
                self._smtp_server = None

    def send_email(self, recipients, subject, body, attachments=None, is_html=False):
        """
        Sends an email with dynamic content and multiple attachments.
        :param recipients: Dictionary with lists for 'to', 'cc', 'bcc'.
        :param subject: The subject line of the email.
        :param body: The content of the email.
        :param attachments: List of file paths to attach.
        :param is_html: Set to True if the body is HTML, False for plain text.
        :return: True if email sent successfully, False otherwise.
        """
        to_recipients = recipients.get('to', [])
        cc_recipients = recipients.get('cc', [])
        bcc_recipients = recipients.get('bcc', [])

        all_recipients = to_recipients + cc_recipients + bcc_recipients
        if not all_recipients:
            logger.error("No recipients specified for email.")
            return False

        # Validate attachments existence before attempting connection
        if attachments:
            for attachment_path in attachments:
                if not os.path.exists(attachment_path):
                    logger.error(f"Required attachment file not found: {attachment_path}. Failing task.")
                    return False

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['Subject'] = subject
        msg['To'] = ", ".join(to_recipients)
        if cc_recipients:
            msg['Cc'] = ", ".join(cc_recipients)
        # Note: BCC is strictly not included in headers to preserve confidentiality

        msg.attach(MIMEText(body, 'html' if is_html else 'plain', 'utf-8'))

        if attachments:
            for attachment_path in attachments:
                try:
                    with open(attachment_path, "rb") as f:
                        filename = os.path.basename(attachment_path)
                        part = MIMEApplication(f.read(), Name=filename)
                        part['Content-Disposition'] = f'attachment; filename="{filename}"'
                        msg.attach(part)
                        logger.info(f"Attached file: {attachment_path}")
                except Exception as e:
                    logger.error(f"Error attaching file {attachment_path}: {e}")
                    return False

        if self.dry_run:
            logger.info(
                f"[DRY-RUN] Simulated email send to TO: {to_recipients}, CC: {cc_recipients}, BCC: {bcc_recipients}. "
                f"Subject: '{subject}', Attachments count: {len(attachments) if attachments else 0}."
            )
            return True

        if not self._connect_smtp():
            return False

        try:
            self._smtp_server.send_message(msg, from_addr=self.sender_email, to_addrs=all_recipients)
            logger.info(f"Email sent successfully to {', '.join(to_recipients)} (CC: {', '.join(cc_recipients)}). Subject: '{subject}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to send email. Error: {e}")
            return False
        finally:
            self._disconnect_smtp()

    def _connect_imap(self):
        """Establishes and logs into the IMAP server."""
        if self.dry_run:
            logger.info("[DRY-RUN] Simulating IMAP connection and authentication.")
            return True
        if self._imap_mail:
            return True
        try:
            self._imap_mail = imaplib.IMAP4_SSL(self.imap_server, timeout=30)
            self._imap_mail.login(self.sender_email, self.sender_password)
            logger.info("Successfully connected and logged into IMAP server.")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP authentication failed. Check credentials. Error: {e}")
            self._imap_mail = None
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during IMAP connect/login: {e}")
            self._imap_mail = None
            return False

    def _disconnect_imap(self):
        """Disconnects from the IMAP server."""
        if self.dry_run:
            logger.info("[DRY-RUN] Simulating IMAP disconnection.")
            return
        if self._imap_mail:
            try:
                self._imap_mail.logout()
                logger.info("Disconnected from IMAP server.")
            except Exception as e:
                logger.warning(f"Error during IMAP disconnection: {e}")
            finally:
                self._imap_mail = None

    def search_emails(self, mailbox='INBOX', criteria='UNSEEN', from_sender=None, subject_contains=None):
        """
        Searches for emails based on criteria using IMAP UIDs.
        Returns a list of email UIDs (bytes).
        """
        if self.dry_run:
            logger.info(
                f"[DRY-RUN] Searching mailbox '{mailbox}' with criteria='{criteria}', "
                f"from='{from_sender}', subject='{subject_contains}'."
            )
            # In dry-run, return a simulated UID for offline workflow demonstration
            return [b"101"]

        if not self._connect_imap():
            return []

        try:
            self._imap_mail.select(mailbox)
            search_query = [criteria]
            if from_sender:
                search_query.extend(['FROM', from_sender])
            if subject_contains:
                search_query.extend(['SUBJECT', subject_contains])

            # Use uid('SEARCH', ...) consistently for unique identifier semantics
            status, email_ids = self._imap_mail.uid('SEARCH', None, *search_query)
            if status != 'OK':
                logger.error(f"IMAP UID search failed. Status: {status}")
                return []

            uids = email_ids[0].split()
            logger.info(f"Found {len(uids)} emails matching criteria in '{mailbox}'.")
            return uids
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
        finally:
            self._disconnect_imap()

    def fetch_email_content(self, uid, mark_as_read=True, download_attachments_dir=None):
        """
        Fetches the content of a specific email by UID.
        Optionally marks as read and downloads attachments.
        """
        uid_str = uid.decode('utf-8') if isinstance(uid, bytes) else str(uid)
        uid_bytes = uid if isinstance(uid, bytes) else str(uid).encode('utf-8')

        if self.dry_run:
            logger.info(f"[DRY-RUN] Fetching simulated email content for UID {uid_str}.")
            # Build simulated attachments and content
            attachments_meta = []
            if download_attachments_dir:
                ensure_directory_exists(download_attachments_dir)
                simulated_file = os.path.join(download_attachments_dir, "sales_report_incoming.pdf")
                with open(simulated_file, "wb") as f:
                    f.write(b"%PDF-1.4 simulated downloaded attachment payload")
                attachments_meta.append({
                    "filename": "sales_report_incoming.pdf",
                    "filepath": simulated_file
                })

            return {
                "uid": uid_str,
                "sender": self.sender_email,
                "subject": "Data Request for 2026-10-14 - Urgent",
                "text_body": "Hello Agent,\n\nWe need the latest data for 2026-10-14. Please process urgently. This is an urgent request for new data processing.\n\nThank you,\nClient Team",
                "html_body": "",
                "has_attachments": True,
                "attachments_meta": attachments_meta
            }

        if not self._connect_imap():
            return None

        try:
            self._imap_mail.select('INBOX')
            status, msg_data = self._imap_mail.uid('FETCH', uid_bytes, '(RFC822)')
            if status != 'OK' or not msg_data or not msg_data[0]:
                logger.error(f"Failed to fetch email UID {uid_str}. Status: {status}")
                return None

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            sender = self._decode_header_part(msg.get('From', ''))
            subject = self._decode_header_part(msg.get('Subject', ''))

            email_text_body = ""
            email_html_body = ""
            attachments_meta = []

            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                raw_filename = part.get_filename()

                if raw_filename and ("attachment" in content_disposition or part.get_content_maintype() != 'multipart'):
                    decoded_filename = self._decode_header_part(raw_filename)
                    # Security: Sanitize filename to prevent directory traversal
                    clean_filename = os.path.basename(decoded_filename).replace("..", "").strip() or "attachment.dat"

                    if download_attachments_dir:
                        ensure_directory_exists(download_attachments_dir)
                        filepath = os.path.join(download_attachments_dir, clean_filename)
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                with open(filepath, "wb") as f:
                                    f.write(payload)
                                attachments_meta.append({'filename': clean_filename, 'filepath': filepath})
                                logger.info(f"Downloaded attachment safely: {filepath}")
                        except Exception as e:
                            logger.error(f"Error downloading attachment {clean_filename}: {e}")
                    else:
                        attachments_meta.append({'filename': clean_filename, 'filepath': None})
                elif "text/plain" in content_type and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        email_text_body += payload.decode(charset, errors='replace')
                    except Exception as e:
                        logger.warning(f"Could not decode text/plain part from UID {uid_str}: {e}")
                elif "text/html" in content_type and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        email_html_body += payload.decode(charset, errors='replace')
                    except Exception as e:
                        logger.warning(f"Could not decode text/html part from UID {uid_str}: {e}")

            if mark_as_read:
                self._imap_mail.uid('STORE', uid_bytes, '+FLAGS', '\\Seen')
                logger.info(f"Marked email UID {uid_str} as read.")

            return {
                "uid": uid_str,
                "sender": sender,
                "subject": subject,
                "text_body": email_text_body,
                "html_body": email_html_body,
                "has_attachments": bool(attachments_meta),
                "attachments_meta": attachments_meta
            }
        except Exception as e:
            logger.error(f"Error fetching/parsing email UID {uid_str}: {e}")
            return None
        finally:
            self._disconnect_imap()

    def _decode_header_part(self, header_value):
        """Decodes MIME encoded header strings safely."""
        if not header_value:
            return ""
        decoded_parts = decode_header(header_value)
        decoded_string = ""
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_string += part.decode(charset if charset else 'utf-8', errors='replace')
                except Exception:
                    decoded_string += part.decode('latin-1', errors='replace')
            else:
                decoded_string += str(part)
        return decoded_string.strip()
