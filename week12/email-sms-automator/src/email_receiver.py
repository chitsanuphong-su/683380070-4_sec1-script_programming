import email
from email.header import decode_header
import imaplib
import os
import re
from typing import Any, Dict, List, Optional

try:
    from .utils import ensure_directory_exists, setup_logging
except ImportError:
    from utils import ensure_directory_exists, setup_logging

logger = setup_logging(__name__)


class EmailReceiver:
    """
    Handles receiving and parsing emails via IMAP.
    Uses consistent UID-based operations.
    Supports live network fetching and simulated dry-run mode.
    """

    def __init__(
        self,
        imap_server: str,
        sender_email: str,
        sender_password: str,
        dry_run: bool = False,
    ):
        self.imap_server = imap_server
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.dry_run = dry_run
        self.mail: Optional[imaplib.IMAP4_SSL] = None
        self._dry_run_messages: Dict[bytes, Dict[str, Any]] = {}
        logger.info(
            f"EmailReceiver initialized for {sender_email} via {imap_server} (dry_run={self.dry_run})."
        )

    def _connect(self) -> bool:
        """Establishes and logs into the IMAP server over SSL."""
        if self.dry_run:
            logger.info("[DRY RUN] Simulating IMAP SSL connection and login.")
            return True

        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.sender_email, self.sender_password)
            logger.info("Successfully connected and logged into IMAP server.")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP authentication failed. Check email and app password. Error: {e}")
            self.mail = None
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during IMAP connect/login: {e}")
            self.mail = None
            return False

    def _disconnect(self) -> None:
        """Disconnects safely from the IMAP server."""
        if self.dry_run:
            logger.info("[DRY RUN] Simulating IMAP disconnection.")
            self.mail = None
            return

        if self.mail:
            try:
                self.mail.logout()
                logger.info("Disconnected from IMAP server.")
            except Exception as e:
                logger.warning(f"Error during IMAP disconnection: {e}")
            finally:
                self.mail = None

    def search_emails(
        self,
        mailbox: str = "INBOX",
        criteria: str = "UNSEEN",
        from_sender: Optional[str] = None,
        subject_contains: Optional[str] = None,
    ) -> List[bytes]:
        """
        Searches for emails based on criteria using UID search.
        :param mailbox: Mailbox to search (e.g., 'INBOX').
        :param criteria: IMAP search criteria (e.g., 'UNSEEN', 'ALL', 'SEEN').
        :param from_sender: Filter by sender email address.
        :param subject_contains: Filter by subject line containing this string.
        :return: A list of email UIDs as bytes (e.g. [b'1', b'2']).
        """
        if self.dry_run:
            logger.info(
                f"[DRY RUN] Simulating IMAP search in '{mailbox}' (criteria={criteria}, "
                f"from={from_sender}, subject={subject_contains})."
            )
            # Filter simulated dry-run messages
            matching_uids = []
            for uid, msg_info in self._dry_run_messages.items():
                if criteria == "UNSEEN" and msg_info.get("seen", False):
                    continue
                if from_sender and from_sender.lower() not in msg_info.get("from", "").lower():
                    continue
                if subject_contains and subject_contains.lower() not in msg_info.get("subject", "").lower():
                    continue
                matching_uids.append(uid)
            logger.info(f"[DRY RUN] Found {len(matching_uids)} simulated matching email(s).")
            return matching_uids

        if not self._connect():
            return []

        try:
            self.mail.select(mailbox)
            search_query = [criteria]
            if from_sender:
                search_query.extend(["FROM", f'"{from_sender}"'])
            if subject_contains:
                search_query.extend(["SUBJECT", f'"{subject_contains}"'])

            # Use UID search consistently
            status, email_ids = self.mail.uid("search", None, *search_query)
            if status != "OK":
                logger.error(f"IMAP UID search failed. Status: {status}")
                return []

            if not email_ids or not email_ids[0]:
                logger.info(f"Found 0 emails matching criteria in '{mailbox}'.")
                return []

            uids = email_ids[0].split()
            logger.info(f"Found {len(uids)} email(s) matching criteria in '{mailbox}'.")
            return uids
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
        finally:
            self._disconnect()

    def fetch_email_content(
        self,
        uid: bytes,
        mark_as_read: bool = True,
        download_attachments_dir: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetches the content of a specific email by UID.
        Optionally marks as read and downloads attachments safely.
        :param uid: The unique ID of the email (bytes or str).
        :param mark_as_read: If True, marks the email as SEEN.
        :param download_attachments_dir: Directory to save attachments, or None to skip.
        :return: A dictionary containing email details or None.
        """
        if isinstance(uid, str):
            uid_bytes = uid.encode("utf-8")
        else:
            uid_bytes = uid

        uid_str = uid_bytes.decode("utf-8", errors="replace")

        if self.dry_run:
            logger.info(f"[DRY RUN] Simulating email fetch for UID {uid_str}.")
            msg_info = self._dry_run_messages.get(uid_bytes)
            if not msg_info:
                logger.error(f"[DRY RUN] Email UID {uid_str} not found in simulated store.")
                return None

            downloaded = []
            if download_attachments_dir and "attachment_data" in msg_info:
                ensure_directory_exists(download_attachments_dir)
                raw_filename = msg_info.get("attachment_filename", "simulated_attachment.pdf")
                safe_filename = self._sanitize_filename(raw_filename)
                save_path = os.path.join(download_attachments_dir, safe_filename)
                with open(save_path, "wb") as f:
                    f.write(msg_info["attachment_data"])
                downloaded.append(save_path)
                logger.info(f"[DRY RUN] Downloaded simulated attachment: {save_path}")

            if mark_as_read:
                msg_info["seen"] = True
                logger.info(f"[DRY RUN] Marked email UID {uid_str} as read.")

            body = msg_info.get("body", "")
            return {
                "uid": uid_str,
                "sender": msg_info.get("from", ""),
                "subject": msg_info.get("subject", ""),
                "body_snippet": body[:200] + "..." if len(body) > 200 else body,
                "attachments_downloaded": downloaded,
            }

        if not self._connect():
            return None

        try:
            self.mail.select("INBOX")
            # Use UID fetch consistently
            status, msg_data = self.mail.uid("fetch", uid_bytes, "(RFC822)")
            if status != "OK" or not msg_data or not msg_data[0]:
                logger.error(f"Failed to fetch email UID {uid_str}. Status: {status}")
                return None

            raw_email = msg_data[0][1]
            if not isinstance(raw_email, bytes):
                logger.error(f"Invalid email payload format for UID {uid_str}.")
                return None

            msg = email.message_from_bytes(raw_email)
            sender = self._decode_header_part(msg.get("From"))
            subject = self._decode_header_part(msg.get("Subject"))

            email_body = ""
            attachments_downloaded = []

            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition.lower():
                    filename = part.get_filename()
                    if filename and download_attachments_dir:
                        ensure_directory_exists(download_attachments_dir)
                        safe_filename = self._sanitize_filename(filename)
                        filepath = os.path.join(download_attachments_dir, safe_filename)

                        # Prevent path traversal outside destination directory
                        real_dest_dir = os.path.realpath(download_attachments_dir)
                        real_target_file = os.path.realpath(filepath)
                        if not real_target_file.startswith(real_dest_dir):
                            logger.error(f"Unsafe path detected for attachment {filename}. Skipping.")
                            continue

                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                with open(filepath, "wb") as f:
                                    f.write(payload)
                                attachments_downloaded.append(filepath)
                                logger.info(f"Downloaded attachment: {filepath}")
                        except Exception as e:
                            logger.error(f"Error downloading attachment {filename}: {e}")
                elif content_type == "text/plain" and "attachment" not in content_disposition.lower():
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or "utf-8"
                        email_body += payload.decode(charset, errors="replace")
                    except Exception as e:
                        logger.warning(f"Could not decode plain text part for UID {uid_str}: {e}")
                        email_body += "[ undecodable plain text part ]"
                elif content_type == "text/html" and "attachment" not in content_disposition.lower():
                    pass

            if mark_as_read:
                self.mail.uid("store", uid_bytes, "+FLAGS", "(\\Seen)")
                logger.info(f"Marked email UID {uid_str} as read.")

            return {
                "uid": uid_str,
                "sender": sender,
                "subject": subject,
                "body_snippet": email_body[:200] + "..." if len(email_body) > 200 else email_body,
                "attachments_downloaded": attachments_downloaded,
            }
        except Exception as e:
            logger.error(f"Error fetching/parsing email UID {uid_str}: {e}")
            return None
        finally:
            self._disconnect()

    def _decode_header_part(self, header_value: Optional[str]) -> str:
        """Decodes MIME encoded header strings."""
        if header_value is None:
            return ""
        decoded_parts = decode_header(header_value)
        decoded_string = ""
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_string += part.decode(charset if charset else "utf-8", errors="replace")
                except Exception:
                    decoded_string += part.decode("latin-1", errors="replace")
            else:
                decoded_string += str(part)
        return decoded_string.strip()

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitizes attachment filename to prevent directory traversal and illegal characters."""
        # Strip directories
        basename = os.path.basename(filename)
        # Strip illegal characters
        clean_name = re.sub(r'[\\/*?:"<>|]', "_", basename)
        clean_name = clean_name.strip(" .")
        return clean_name or "unnamed_attachment"
