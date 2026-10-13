# Week 11 — LabX ADV: Agentic Document Automation

## 1. Project Overview
This project introduces a deterministic, configuration-driven **Agentic Document Processor** capable of executing automated document workflows across Microsoft Word (`.docx`) and Adobe PDF (`.pdf`) formats. Guiding its actions by reading a declarative JSON plan, the `DocumentAgent` dispatches and monitors tasks sequentially while maintaining a structured audit trail and saving an audit report in JSON.

## 2. Learning Objectives
- Design and implement a configuration-driven **Document Agent** for document processing workflows.
- Master advanced `python-docx` techniques:
  - Template-based document generation with placeholder replacement (supporting multi-run placeholders).
  - Dynamic table insertion at specified anchors (`{{TABLE_PLACEHOLDER}}`) or fallback appending.
  - Full-text extraction from paragraphs and tabular structures.
- Master advanced `PyPDF2` and `ReportLab` techniques:
  - Generating on-the-fly text watermarks with customizable opacity, rotation, and font size matching source page dimensions.
  - Merging multiple PDF documents into an unified publication.
  - Extracting multi-page text content with readable page delineations.
- Implement robust error handling, detailed logging, and comprehensive audit reporting.

## 3. Features
- **Config-Driven Architecture**: Execution logic is dictated entirely by `configs/document_automation_config.json`.
- **Dynamic Watermarking**: ReportLab dynamically creates overlay canvases adapted to source document page sizes without persistent temp file clutter.
- **Robust Placeholder Substitution**: Solves Microsoft Word's multi-run segmentation issue, ensuring placeholders like `{{REPORT_TITLE}}` are seamlessly replaced without losing paragraph formatting.
- **Dynamic Table Injection**: Converts structured list-of-lists data into formatted Word tables with bold headers directly replacing `{{TABLE_PLACEHOLDER}}`.
- **Traceable Audit Logging**: Full audit trail recording timestamps, task types, outcomes, and execution summaries saved as timestamped JSON files in `documents/reports/`.

## 4. Agentic Workflow Architecture
```
JSON Configuration (document_automation_config.json)
        │
        ▼
   ConfigParser
        │
        ▼
   DocumentAgent
        │
        ▼
   Task Dispatcher
   ┌───────────────────────┴───────────────────────┐
   ▼                                               ▼
WordTasks                                       PDFTasks
├── generate_word_report                        ├── apply_pdf_watermark
└── extract_word_text                           ├── merge_pdfs
   │                                            └── extract_pdf_text
   └───────────────────────┬───────────────────────┘
                           │
                           ▼
                      Audit Logger
                           │
                           ▼
          audit_report_YYYYMMDD_HHMMSS.json
```

## 5. Technologies Used
- **Python**: 3.10+
- **PyPDF2**: PDF manipulation, overlay merging, document splitting, and text extraction.
- **python-docx**: DOCX document generation, XML manipulation, and text parsing.
- **ReportLab**: High-fidelity dynamic PDF generation for watermarking overlays.

## 6. Project Structure
```
agentic-document-automator/
├── src/
│   ├── __init__.py           # Python package marker
│   ├── document_agent.py     # Main agent logic (reads config, dispatches tasks)
│   ├── pdf_tasks.py          # Functions for advanced PDF operations
│   ├── word_tasks.py         # Functions for advanced Word operations
│   ├── config_parser.py      # Loads and validates agent configurations
│   └── utils.py              # Logging, directory creation, audit logging
│
├── configs/
│   └── document_automation_config.json  # JSON config for agent's tasks
│
├── templates/
│   └── report_template.docx  # Word document template with placeholders
│
├── documents/
│   ├── source_document.pdf   # Input multi-page PDF for watermarking
│   ├── dummy_doc1.pdf        # Input PDF 1 for merging
│   ├── dummy_doc2.pdf        # Input PDF 2 for merging
│   ├── generated_report.docx # Output Word report
│   ├── watermarked_document.pdf # Output watermarked PDF
│   ├── merged_docs.pdf       # Output merged PDF
│   ├── extracted_pdf_text.txt# Output text extracted from PDF
│   ├── extracted_word_text.txt# Output text extracted from Word
│   └── reports/
│       └── audit_report_YYYYMMDD_HHMMSS.json # Traceable execution audit log
│
├── tests/
│   └── test_agentic_automator.py # Automated test suite
├── main.py                   # Application entry point
├── requirements.txt          # Project dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # Project documentation
```

## 7. Installation
1. Clone or navigate into the workspace repository:
   ```bash
   cd week11/agentic-document-automator
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```
3. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## 8. Configuration Guide
The system configuration resides at `configs/document_automation_config.json`.
### Example Configuration Structure:
```json
{
  "global_data": {
    "REPORT_DATE": "2025-06-15",
    "AUTHOR_NAME": "AI Document Agent",
    "COMPANY_NAME": "Automated Docs Inc."
  },
  "output_files": {
    "generated_report": "documents/generated_report.docx",
    "watermarked_pdf": "documents/watermarked_document.pdf",
    "merged_pdf": "documents/merged_docs.pdf",
    "extracted_pdf_text": "documents/extracted_pdf_text.txt",
    "extracted_word_text": "documents/extracted_word_text.txt"
  },
  "tasks": [
    {
      "name": "Generate Monthly Performance Report",
      "type": "generate_word_report",
      "template_path": "templates/report_template.docx",
      "output_path": "documents/generated_report.docx",
      "data": {
        "REPORT_TITLE": "Monthly Performance Summary",
        "INTRODUCTION_TEXT": "This automated report provides a summary of key performance indicators for the past month.",
        "MONTH_PERIOD": "May 2025"
      },
      "table_data": [
        ["Category", "Value", "Trend"],
        ["Sales Revenue", "$120,000", "Up 10%"],
        ["Customer Acquisition", "500", "Stable"],
        ["Project Completion Rate", "95%", "Excellent"]
      ]
    }
  ]
}
```

## 9. Supported Task Types
1. **`generate_word_report`**: Reads a template `.docx`, replaces placeholders combining `global_data` and task-specific `data`, injects `table_data` into `{{TABLE_PLACEHOLDER}}`, and saves the file.
2. **`apply_pdf_watermark`**: Renders a dynamic watermark overlay with ReportLab matching the input PDF dimensions, overlays it onto each page, and writes the output PDF.
3. **`merge_pdfs`**: Merges an array of input PDFs sequentially into one PDF document.
4. **`extract_word_text`**: Extracts text from all paragraphs and tables of a DOCX document into a plain text file.
5. **`extract_pdf_text`**: Extracts textual content from each page of a PDF document into a text file with page markers.

## 10. How to Run
Execute the main script from the project directory:
```bash
python main.py
```
Or from the workspace root:
```bash
python week11/agentic-document-automator/main.py
```

## 11. Input Documents
- **`templates/report_template.docx`**: Template containing placeholders:
  - `{{REPORT_TITLE}}`
  - `{{REPORT_DATE}}`
  - `{{AUTHOR_NAME}}`
  - `{{COMPANY_NAME}}`
  - `{{INTRODUCTION_TEXT}}`
  - `{{MONTH_PERIOD}}`
  - `{{TABLE_PLACEHOLDER}}`
- **`documents/source_document.pdf`**: Multi-page PDF suitable for text extraction and watermarking.
- **`documents/dummy_doc1.pdf` & `documents/dummy_doc2.pdf`**: Sample PDFs for merging operations.

## 12. Generated Outputs
- `documents/generated_report.docx`: Formatted Word document with replaced placeholders and injected table.
- `documents/watermarked_document.pdf`: 2-page PDF document with semi-transparent "CONFIDENTIAL" watermark.
- `documents/merged_docs.pdf`: Combined PDF merging dummy docs 1 and 2.
- `documents/extracted_word_text.txt`: Plain text dump of the generated Word document.
- `documents/extracted_pdf_text.txt`: Text extracted page-by-page from `source_document.pdf`.
- `documents/reports/audit_report_YYYYMMDD_HHMMSS.json`: Timestamped JSON audit record.

## 13. Audit Logging
Every run logs detailed events in real time. Upon completion, a JSON file in `documents/reports/` records each step with:
- `timestamp`: ISO-8601 timestamp.
- `status`: `INFO`, `SUCCESS`, `WARNING`, `ERROR`, or `CRITICAL`.
- `task_type`: Task identifier.
- `message`: Descriptive message.
- `details`: Task parameters or exception details.

## 14. Testing
Run the automated test suite with:
```bash
python -m unittest discover tests
```
The test suite validates:
- Logging configuration, directory creation, and audit entry recording.
- JSON configuration parsing and validation.
- DOCX template placeholder replacement and table injection.
- PDF watermarking, merging, and text extraction.

## 15. Troubleshooting
- **`FileNotFoundError`**: Verify that paths configured in `document_automation_config.json` exist relative to the project root.
- **`ImportError: No module named 'reportlab'`**: Run `pip install ReportLab` or `pip install -r requirements.txt`.
- **Placeholders not replaced in Word**: The system handles split-run placeholders. Ensure placeholder syntax matches `{{KEY}}` or configured key definitions without accidental spelling mismatches.
- **Table positioning**: Ensure `{{TABLE_PLACEHOLDER}}` is present in the template. If absent, the table is automatically appended to the end of the document.

## 16. Future Enhancements
- Integration with external REST APIs and SQL databases for automated report generation.
- Digital PDF signature application and encrypted password protection.
- PDF form filling capabilities using `pdfrw` or `PyMuPDF`.
- Web UI (Streamlit or FastAPI) for interactive document uploading and workflow orchestration.
