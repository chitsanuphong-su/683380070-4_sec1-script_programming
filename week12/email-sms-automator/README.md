# Week 12 — LabX BASIC: Automating Communications (Email & SMS)

This project demonstrates how to automate sending and receiving emails, sending attachments, and dispatching SMS messages via email-to-SMS carrier gateways using Python. It uses standard network protocols (`smtplib` for SMTP and `imaplib` for IMAP), robust MIME message structures, and secure environment configuration.

---

## 1. Project Overview

Automating communication is essential for real-world production systems such as alerts, daily business reports, status notifications, and customer support bots. This project implements:
- **SMTP Email Transmission**: Sending plaintext and multipart emails with binary attachments (e.g., PDF reports) over secure TLS connections.
- **IMAP Email Processing**: Querying an inbox for unread messages matching specific senders and subjects, fetching and decoding message headers and body parts, downloading attachments safely, and marking processed messages as read.
- **Email-to-SMS Gateways**: Bridging SMS notifications through carrier email gateways without requiring specialized external hardware.
- **Security-First Architecture**: Excluding sensitive credentials from version control via `.env` files and `.gitignore`.
- **Dual Execution Modes**: Safe offline simulation (`DRY RUN`) by default, and explicit live execution (`--live`) with safety warnings.

---

## 2. Learning Objectives

- Understand the fundamentals of internet mail protocols (**SMTP** on port 587 with STARTTLS, **IMAP** on port 993 with SSL).
- Construct MIME messages (`MIMEMultipart`, `MIMEText`, `MIMEApplication`).
- Programmatically search, parse, and process incoming mailbox items using IMAP UID commands.
- Safeguard credentials with Google App Passwords and environment variables.
- Write modular, testable Python code and unit test communication logic safely with mocks.

---

## 3. Features

1. **Modular Architecture**: Separate modules for sending (`EmailSender`), receiving (`EmailReceiver`), SMS routing (`SMSGateway`), and utilities (`utils.py`).
2. **Safe Attachment Handling**: Validates existence before transmission; sanitizes filenames and protects against directory traversal during downloads.
3. **Robust Header Decoding**: Decodes encoded email headers (UTF-8, Latin-1, Base64).
4. **UID-Based IMAP Operations**: Prevents message index collisions by using IMAP UIDs (`uid('search', ...)`, `uid('fetch', ...)`, `uid('store', ...)`).
5. **Dry Run Mode**: Allows testing full business workflows locally without sending actual emails or modifying remote mailboxes.
6. **Automated Testing Suite**: 17 comprehensive unit tests with `pytest` covering normal operations, error handling, and security protections.

---

## 4. Technologies Used

- **Python 3.10+ / 3.13+**
- **Standard Libraries**: `smtplib`, `imaplib`, `email`, `logging`, `os`, `pathlib`, `re`, `argparse`
- **External Dependencies**:
  - `python-dotenv`: Secure configuration loading from `.env`
  - `pytest`: Automated unit test framework and mock verification
  - `reportlab`: Generation of valid sample PDF reports

---

## 5. Project Structure

```
email-sms-automator/
├── src/
│   ├── __init__.py          # Package marker
│   ├── email_sender.py      # SMTP sending logic (class EmailSender)
│   ├── email_receiver.py    # IMAP receiving & parsing logic (class EmailReceiver)
│   ├── sms_gateway.py       # Email-to-SMS routing logic (class SMSGateway)
│   └── utils.py             # Logging, env loading, directory helpers
├── data/
│   ├── attachments/         # Destination folder for downloaded attachments
│   │   └── .gitkeep         # Tracked directory anchor
│   └── dummy_report.pdf     # Sample PDF report for attachment tests
├── tests/
│   ├── test_email_sender.py   # Unit tests for EmailSender
│   ├── test_email_receiver.py # Unit tests for EmailReceiver
│   └── test_sms_gateway.py    # Unit tests for SMSGateway
├── .env                     # Local credentials (DO NOT COMMIT)
├── .env.example             # Safe template for credentials
├── .gitignore               # Excludes secrets, caches, and attachment files
├── main.py                  # Main orchestration script
├── requirements.txt         # Project dependencies
└── README.md                # Comprehensive documentation
```

---

## 6. Installation

### 6.1 Clone or Navigate to the Workspace
```bash
cd week12/email-sms-automator
```

### 6.2 Create and Activate a Virtual Environment
- **Windows (PowerShell / Command Prompt)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 6.3 Install Required Packages
```bash
python -m pip install -r requirements.txt
```

---

## 7. Environment Configuration

1. Copy the provided `.env.example` to `.env`:
   - Windows:
     ```cmd
     copy .env.example .env
     ```
   - Linux/macOS:
     ```bash
     cp .env.example .env
     ```
2. Open `.env` and fill in your configuration:
   ```ini
   SENDER_EMAIL=your_email@gmail.com
   SENDER_APP_PASSWORD=your_app_password

   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587

   IMAP_SERVER=imap.gmail.com

   TEST_RECIPIENT_EMAIL=recipient@example.com

   TEST_SMS_PHONE_NUMBER=1234567890
   TEST_SMS_CARRIER=att
   ```

> [!IMPORTANT]
> **For Gmail Users:** Do NOT use your primary Google Account password.
> 1. Ensure **2-Step Verification** is enabled on your Google Account.
> 2. Go to Google Account > Security > **App passwords**.
> 3. Create an App password (e.g. named "Python Automator").
> 4. Paste the 16-character code into `SENDER_APP_PASSWORD`.

---

## 8. SMTP Email Sending (`src/email_sender.py`)

The `EmailSender` class manages the lifecycle of SMTP connections:
- Connects using `smtplib.SMTP(host, port)`.
- Initiates TLS encryption via `server.starttls()`.
- Authenticates with `server.login(user, password)`.
- Packs message bodies and attachments into `MIMEMultipart`.
- Automatically quits the connection in a `finally` block.

---

## 9. IMAP Email Receiving (`src/email_receiver.py`)

The `EmailReceiver` class manages incoming email retrieval:
- Establishes SSL connections with `imaplib.IMAP4_SSL(server)`.
- Performs searches via `mail.uid('search', None, *criteria)`.
- Fetches messages using `mail.uid('fetch', uid, '(RFC822)')`.
- Traverses message parts (`msg.walk()`) to extract plaintext and attachments.
- Sanitizes file paths before saving to prevent directory traversal.
- Flags emails as read using `mail.uid('store', uid, '+FLAGS', '(\\Seen)')`.

---

## 10. SMS Gateway (`src/sms_gateway.py`)

The `SMSGateway` routes SMS messages via carrier-specific email domains:
| Carrier | Domain Gateway | Example Recipient |
| :--- | :--- | :--- |
| AT&T | `@txt.att.net` | `1234567890@txt.att.net` |
| Verizon | `@vtext.com` | `1234567890@vtext.com` |
| T-Mobile | `@tmomail.net` | `1234567890@tmomail.net` |
| Sprint | `@messaging.sprintpcs.com` | `1234567890@messaging.sprintpcs.com` |
| Boost Mobile | `@sms.boostmobile.com` | `1234567890@sms.boostmobile.com` |
| Cricket | `@mms.cricketwireless.net` | `1234567890@mms.cricketwireless.net` |
| US Cellular | `@email.uscc.net` | `1234567890@email.uscc.net` |

---

## 11. Sample PDF Attachment

A sample report file (`data/dummy_report.pdf`) is pre-generated using ReportLab.
To re-generate it at any time:
```bash
python -c "from reportlab.lib.pagesizes import letter; from reportlab.pdfgen import canvas; c = canvas.Canvas('data/dummy_report.pdf', pagesize=letter); c.setFont('Helvetica-Bold', 18); c.drawString(100, 750, 'AUTOMATED COMMUNICATION REPORT'); c.setFont('Helvetica', 12); c.drawString(100, 720, 'Week 12 - LabX BASIC'); c.drawString(100, 690, 'This PDF is a sample attachment generated for testing automated email communication.'); c.drawString(100, 660, 'Project: Email & SMS Automator'); c.drawString(100, 630, 'Purpose: Demonstrate sending email attachments using Python.'); c.save()"
```

---

## 12. Execution Modes

### 12.1 Dry Run Mode (Default)
Safe simulation without connecting to remote servers or sending live emails:
```bash
python main.py
```
Outputs simulation logs for:
- Connecting to SMTP and IMAP
- Sending plaintext email
- Attaching and sending PDF report
- Resolving SMS carrier address
- Searching simulated incoming inbox and downloading attachment
- Marking incoming demo message as read

### 12.2 Live Mode
Connects to real SMTP/IMAP servers and sends actual communications:
```bash
python main.py --live
```
> [!WARNING]
> Requires real credentials in `.env` and internet connectivity. Do not run without prior authorization.

---

## 13. Automated Testing

Run the unit test suite using `pytest`:
```bash
python -m pytest -q
```
Expected output:
```
.................                                                        [100%]
17 passed in 0.07s
```

Test coverage includes:
- Plaintext and HTML email creation
- Missing attachment error handling
- SMTP authentication and connection failure handling
- IMAP UID search and fetch
- Multipart email parsing and header decoding
- Attachment download and filename sanitization (directory traversal prevention)
- SMS carrier gateway resolution and input validation

---

## 14. Security Considerations

- **Never Commit Secrets**: `.env` and credential files are excluded in `.gitignore`.
- **Sanitized Attachment File Paths**: Downloaded filenames are sanitized and validated to remain strictly inside `data/attachments/`.
- **App Passwords**: Avoid using raw Google account passwords.
- **TLS/SSL Encryption**: All network communications use TLS (SMTP STARTTLS) and SSL (IMAP SSL).

---

## 15. Troubleshooting

- **`ValueError: Environment variable '...' not set`**: Verify `.env` exists in the project root and contains all required keys.
- **`SMTPAuthenticationError`**: Ensure you generated and entered a 16-character Google App Password, not your standard login password.
- **`SMTPConnectError` / `IMAP4.error`**: Check your network connection, firewall settings, and port configuration (SMTP: 587, IMAP: 993).
- **Attachments Missing**: Ensure `data/dummy_report.pdf` exists before executing.

---

## 16. Known Limitations

- **Carrier Gateway Support**: Many modern telecom providers outside the US (including Thailand) do not provide public email-to-SMS gateways.
- **Delivery Guarantee**: SMTP acceptance by a carrier gateway does not guarantee final SMS delivery to the handset.

---

## 17. Future Extensions

- **Scheduling**: Integrate with `APScheduler` or `schedule` for daily automated report dispatches.
- **Template Engines**: Use `Jinja2` to dynamically format HTML email notifications.
- **Commercial SMS APIs**: Integrate with Twilio, AWS SNS, or Vonage for global SMS delivery receipts.
- **Incoming Webhooks**: Replace IMAP polling with webhook push notifications.
