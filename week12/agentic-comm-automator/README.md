# Week 12 — LabX ADV: Agentic Communication Workflows (Advanced Email & SMS)

An autonomous, configuration-driven **CommunicationAgent** built in Python that orchestrates complex email and SMS automation workflows without requiring external LLM APIs. The system coordinates dynamic content templating, conditional notifications, multi-recipient transmissions, IMAP inbox monitoring with rule-based auto-replies, and comprehensive JSON audit logging.

---

## 1. Project Overview

The **Agentic Communication Automator** elevates basic email and SMS messaging into an agentic paradigm. Rather than running linear, hardcoded communication scripts, workflows are defined declaratively in a JSON specification file (`comm_pipeline_config.json`). 

A centralized `CommunicationAgent` reads the pipeline, dynamically evaluates template placeholders using shared runtime context, securely executes email and SMS tasks, applies if-then business rules on incoming emails, chains outputs between tasks, and generates structured audit reports.

---

## 2. Learning Objectives

- **Agentic Workflow Orchestration**: Design a centralized, modular agent capable of coordinating sequential tasks and handling dependencies.
- **Declarative Configuration**: Separate business workflow definitions from core engine logic via JSON pipelines.
- **Dynamic Content Generation**: Master template substitution supporting context variables, custom formatting specs (`{sales_figure:.2f}`), nested dictionary/list traversal (`{attachments_meta.0.filepath}`), and safe environment variables (`${VAR}`).
- **Advanced Email Management**: Send multi-recipient messages (To, CC, BCC) with MIME attachments, and process IMAP mailboxes via UID-based search, parsing, and attachment downloads.
- **Rule-Based Automation**: Implement intelligent if-then matching rules on subject, body, sender, and attachment presence to trigger automated SMS alerts and auto-replies while preventing infinite loops.
- **Security & Safe Execution**: Support strict credential isolation, sensitive data redaction, and default safe offline dry-run execution.

---

## 3. Basic vs Advanced Comparison

| Feature / Trait | LabX BASIC (`email-sms-automator`) | LabX ADV (`agentic-comm-automator`) |
| :--- | :--- | :--- |
| **Execution Paradigm** | Procedural / Hardcoded Python scripts | Declarative JSON configuration workflow |
| **Architecture** | Direct standalone functions | Modular `CommunicationAgent` with task dispatcher |
| **Context Management** | Isolated variable scope | Shared agent context (`self.context`) with task output chaining |
| **Content Generation** | Basic string concatenation | Robust template rendering with formatting and nested path access |
| **Recipient Handling** | Single destination email | Multiple recipients (`to`, `cc`, `bcc`) |
| **Attachments** | Single static attachment | Multiple dynamic attachments with pre-flight validation |
| **Inbox Processing** | Basic sequential reading | Rule-based engine (IF conditions $\rightarrow$ THEN actions) |
| **Auto-Replies & Alerts** | Not supported | Automated dynamic email replies and conditional SMS alerts |
| **Infinite Loop Guard** | N/A | Strict reply-loop detection and sender validation |
| **Audit & Logging** | Console print statements | Structured JSON audit reports with execution statistics |
| **Execution Safety** | Requires network credentials | Default offline Dry-Run simulation mode + opt-in `--live` mode |

---

## 4. Agent Architecture

```
                  main.py / CLI
                        |
                        v
                   ConfigParser
                        |
                        v
             comm_pipeline_config.json
                        |
                        v
              CommunicationAgent
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
   Shared Context   Dispatcher    Audit Logging
   (State Chaining)     |         (JSON Reports)
                        |
         +--------------+---------------+
         |              |               |
         v              v               v
     EmailTasks     SMSTasks       Inbox Rules
    (SMTP/IMAP)   (SMS Gateway)     Engine
         |              |               |
         v              v               v
     SMTP Server   Email-to-SMS   IMAP Mailbox
      (Outbound)      Gateway      (Inbound)
```

### Component Roles:
1. **`ConfigParser`**: Validates JSON schema, task types, recipient structures, and rule syntax.
2. **`TemplateRenderer`**: Resolves `{key}`, `{key:format}`, `{nested.path}`, and safe `${ENV_VAR}` tokens.
3. **`CommunicationAgent`**: Orchestrates sequential task dispatch, context chaining, and rule evaluations.
4. **`EmailTasks`**: Manages secure SMTP (TLS) and IMAP (SSL) protocols using UIDs.
5. **`SMSTasks`**: Resolves carrier SMS gateway addresses and delegates transmission to `EmailTasks`.
6. **`Utils`**: Formats audit entries, manages directories, and loads environment variables.

---

## 5. Project Structure

```
week12/agentic-comm-automator/
│
├── configs/
│   └── comm_pipeline_config.json         # Declarative workflow specification
│
├── data/
│   ├── attachments/
│   │   └── .gitkeep                      # Outgoing attachment store
│   ├── incoming_attachments/
│   │   └── .gitkeep                      # Downloaded incoming attachments
│   └── reports/
│       ├── sales_report.pdf              # Sample PDF attachment (ReportLab)
│       └── summary_data.xlsx             # Sample Excel data (openpyxl)
│
├── reports/
│   └── .gitkeep                          # Output directory for audit reports
│
├── src/
│   ├── __init__.py                       # Package initializer
│   ├── communication_agent.py            # Central orchestrator & rule engine
│   ├── config_parser.py                  # Pipeline validator & loader
│   ├── email_tasks.py                    # SMTP sending & IMAP UID handling
│   ├── sms_tasks.py                      # Carrier SMS gateway interface
│   ├── template_renderer.py              # Template rendering engine
│   └── utils.py                          # Logging, env loader, directory helpers
│
├── tests/
│   ├── test_communication_agent.py       # End-to-end and agent unit tests
│   ├── test_config_parser.py             # Schema & syntax validation tests
│   ├── test_email_tasks.py               # SMTP/IMAP logic & mock tests
│   ├── test_sms_tasks.py                 # Carrier gateway conversion tests
│   └── test_template_renderer.py         # Template placeholder & security tests
│
├── .env.example                          # Environment variable template
├── .gitignore                            # Git exclusion rules (credentials & caches)
├── generate_sample_reports.py            # Utility to generate sample PDF/XLSX
├── main.py                               # CLI entry point
├── requirements.txt                      # Python dependencies
└── README.md                             # Comprehensive technical documentation
```

---

## 6. Technologies Used

- **Python 3.13 / 3.10+**: Core programming language.
- **smtplib & imaplib**: Standard library modules for email protocols with SSL/TLS.
- **email**: Standard MIME multipart construction and header decoding.
- **python-dotenv**: Safe `.env` variable loading.
- **ReportLab**: Programmatic PDF report generation.
- **openpyxl**: Structured spreadsheet (`.xlsx`) generation and parsing.
- **pytest**: Automated unit and integration testing suite.

---

## 7. Installation & Setup

1. **Navigate to the target directory:**
   ```bash
   cd week12/agentic-comm-automator
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install required dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Verify sample data files:**
   Sample PDF and XLSX files are pre-generated. If needed, re-generate them via:
   ```bash
   python generate_sample_reports.py
   ```

---

## 8. Environment Configuration

Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```

Configurable variables:
```ini
# Gmail / Email Account Credentials
SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_gmail_app_password

# Server Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
IMAP_SERVER=imap.gmail.com

# Test Destinations
TEST_RECIPIENT_EMAIL=recipient@example.com
TEST_SMS_PHONE_NUMBER=1234567890
TEST_SMS_CARRIER=att
```

> **Security Reminder:**
> - Never commit `.env` to Git. The repository's `.gitignore` automatically excludes it.
> - For Gmail, use an **App Password** with 2-Step Verification enabled.

---

## 9. JSON Workflow Configuration

The workflow is defined in `configs/comm_pipeline_config.json` with 4 chained tasks:

1. **Task 1 (`send_email`)**: Send Daily Sales Report Email with PDF and XLSX attachments to `TEST_RECIPIENT_EMAIL` (CC: `SENDER_EMAIL`).
2. **Task 2 (`send_sms`)**: Send SMS alert with dynamic sales figures and customer count via carrier gateway.
3. **Task 3 (`send_email`)**: Simulate an incoming urgent data request email with an attachment sent to `SENDER_EMAIL`. Saves output to context key `simulated_email_sent`.
4. **Task 4 (`process_inbox`)**: Search UNSEEN emails matching `Data Request` from `SENDER_EMAIL`.
   - **Rule 1 (Urgent Alert)**: If subject contains "Urgent" and email has attachments $\rightarrow$ Download attachment to `data/incoming_attachments` and dispatch SMS alert.
   - **Rule 2 (Automated Reply)**: If body contains "new data processing" $\rightarrow$ Transmit automated response `Re: {subject} - Received & Processing`.

---

## 10. Execution Modes

### 10.1 Default Mode — Dry Run (Offline & Safe)
By default, running `main.py` executes in **Dry-Run mode**. No actual network calls or email transmissions occur:
```bash
python main.py
```
- Validates all pipeline parameters and checks attachment existence.
- Simulates SMTP message construction, envelope handling, and attachment bundling.
- Simulates IMAP search, content extraction, attachment download, and rule matching.
- Evaluates auto-reply and SMS alert logic.
- Writes a complete audit trail to `reports/audit_report_comm_YYYYMMDD_HHMMSS.json`.

### 10.2 Live Mode (Explicit Authorization Required)
To run live tasks against real email and carrier servers:
```bash
python main.py --live
```
*Note: Ensure valid credentials exist in `.env` before running in live mode.*

---

## 11. Automated Testing

Run the test suite using pytest:
```bash
python -m pytest -v
```

All 28 automated tests run completely offline and mock external services:
- **`test_config_parser.py`**: Schema validations, error detection for missing keys, malformed JSON, and rule structures.
- **`test_template_renderer.py`**: Placeholder substitution, nested list/dict traversal, formatting syntax, and unauthorized environment variable access prevention.
- **`test_email_tasks.py`**: Recipient handling (To/CC/BCC), MIME attachment assembly, missing file error propagation, IMAP UID search and decoding.
- **`test_sms_tasks.py`**: Carrier gateway resolution, direct gateway formatting, and multi-recipient transmission.
- **`test_communication_agent.py`**: End-to-end 4-task pipeline execution in dry-run mode, context chaining, and audit log generation.

---

## 12. Security Considerations

1. **Credential Isolation**: App passwords and tokens are loaded strictly via environment variables.
2. **Audit Sanitization**: Passwords, tokens, and raw private credentials are automatically redacted (`******`) from audit logs.
3. **Anti-Traversal Attachment Handling**: File downloads sanitize attachment filenames via `os.path.basename` and strip directory traversal sequences (`..`).
4. **Auto-Reply Loop Prevention**: Auto-replies check subject chains (`Re: Re:`) and filter messages from automated loopback addresses.
5. **Restricted Template Scope**: Templates cannot invoke arbitrary Python methods or access unapproved system environment variables.

---

## 13. Future Enhancements

- **Jinja2 Templating**: Support loops, conditions, and dynamic tables within HTML email bodies.
- **NLP Intent Recognition**: Integrate lightweight NLP (`spaCy`) to classify email sentiment and extract structured request entities.
- **Persistent Database Storage**: Log email history, thread IDs, and metrics into SQLite or PostgreSQL.
- **Webhook & Event Triggers**: Integrate webhook listeners or file watchers (`watchdog`) to run agent tasks event-driven.
