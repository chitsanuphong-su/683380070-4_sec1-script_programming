# Week 11 — LabX BASIC: Automating PDFs & Word Documents

This project demonstrates how to automate common tasks involving PDF and Word documents using Python. It leverages `PyPDF2` for PDF manipulation (text extraction, splitting, and merging) and `python-docx` for programmatic Word document creation, formatting, and report generation.

---

## 1. Project Overview

Document-heavy business processes often require repetitive extraction of data from PDF files and synthesis into structured Word reports. This project provides a modular, reliable Python prototype that:
- Ingests PDF documents and extracts raw text cleanly across multiple pages.
- Assembles rich `.docx` reports featuring headings, custom paragraph formatting (bold, italic, alignment, font sizes), and structured summary tables.
- Demonstrates batch PDF manipulation including file merging and multi-page splitting.

---

## 2. Learning Objectives

- Understand the programmatic structure and limitations of PDF and Word document formats.
- Master the `PyPDF2` library for reading, manipulating (merging, splitting), and extracting text from PDF files.
- Master the `python-docx` library for creating, modifying, and formatting `.docx` Word documents (headings, paragraphs, runs, tables).
- Develop practical automation scripts for common document workflows like report generation, content extraction, and document assembly.
- Implement robust error handling, diagnostic logging, and clean package architecture.

---

## 3. Features

- **PDF Text Extraction**: Extracts text across all pages with readable page demarcation. Safely handles pages with empty or non-extractable text.
- **Word Report Generation**: Creates clean `.docx` reports containing:
  - Custom headings (Level 1, Level 2).
  - Formatted introductory notices (bold, italicized, styled runs, alignment).
  - Cleanly integrated extracted text.
  - Formatted summary metrics table with custom column widths and bold headers.
- **PDF Merging**: Combines multiple independent PDF documents into a single sequential PDF file.
- **PDF Splitting**: Splits a multi-page PDF into smaller documents based on specified chunk size (`pages_per_split`).
- **Comprehensive Logging & Utilities**: Centralized logging with timestamps and automated directory creation.

---

## 4. Technologies Used

- **Python 3.10+** (tested on Python 3.13)
- **PyPDF2**: PDF reading, text extraction, page manipulation, merging, and splitting.
- **python-docx**: Programmatic creation and styling of Microsoft Word (.docx) documents.
- **reportlab**: Utility used to synthesize sample input PDF documents for automated verification.

---

## 5. Project Structure

```text
document-automator/
├── src/
│   ├── __init__.py           # Python package marker
│   ├── pdf_processor.py      # Logic for PyPDF2 operations (extract, merge, split)
│   ├── word_processor.py     # Logic for python-docx operations (create, format, tables)
│   └── utils.py              # General utilities (logging, directory creation)
├── documents/
│   ├── input_article.pdf     # Sample 2-page PDF for text extraction
│   ├── dummy_doc1.pdf        # Sample PDF for merge testing
│   ├── dummy_doc2.pdf        # Sample PDF for merge testing
│   ├── output_report.docx    # Generated Word document
│   └── merged_output.pdf     # Generated merged PDF
├── tests/
│   ├── __init__.py
│   └── test_automation.py    # Unit & integration test suite
├── generate_samples.py       # Helper script to create sample input PDFs
├── main.py                   # Application entry point orchestrating workflow
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore configuration
└── README.md                 # Project documentation
```

---

## 6. Installation Instructions

1. **Navigate to the project directory:**
   ```bash
   cd week11/document-automator
   ```

2. **(Optional) Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 7. How to Run

### Main Workflow
Execute the automation pipeline directly using:
```bash
python main.py
```

### Running Automated Tests
Run the comprehensive test suite verifying extraction, generation, merge, split, and error handling:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 8. Input Documents

The `documents/` folder contains the sample inputs:
- `input_article.pdf`: A 2-page document covering an Introduction to Automation (Page 1) and Benefits of Automation with a Conclusion (Page 2).
- `dummy_doc1.pdf`: Single-page document labeled *"Dummy Document 1 - PDF Merging Test"*.
- `dummy_doc2.pdf`: Single-page document labeled *"Dummy Document 2 - PDF Merging Test"*.

If you need to regenerate these sample files at any time:
```bash
python generate_samples.py
```

---

## 9. Generated Outputs

Running `python main.py` produces:
1. `documents/output_report.docx`:
   - Title heading: *Automated Document Report*
   - Subtitle & notice: formatted with bold and centered italic text.
   - Body: Extracted content from `input_article.pdf`.
   - Summary section: Level 2 heading with a 3-column table displaying metrics (`Total Pages Processed`, `Document Type`, `Generated Date`).
2. `documents/merged_output.pdf`:
   - Sequential 2-page PDF joining `dummy_doc1.pdf` and `dummy_doc2.pdf`.

---

## 10. Example Workflow

```
[Start]
  │
  ├─► Check documents/input_article.pdf
  ├─► Extract text with PDFProcessor
  │
  ├─► Create docx with WordProcessor
  ├─► Add Title, Notices & Extracted text
  ├─► Append Summary Table
  ├─► Save documents/output_report.docx
  │
  ├─► Verify dummy_doc1.pdf & dummy_doc2.pdf
  ├─► Merge with PDFProcessor
  └─► Save documents/merged_output.pdf
[Completed]
```

---

## 11. Troubleshooting

- **`FileNotFoundError`**: Verify that input PDFs (`input_article.pdf`, `dummy_doc1.pdf`, `dummy_doc2.pdf`) are located inside the `documents/` folder.
- **`PyPDF2.errors.PdfReadError`**: Occurs if the PDF is malformed or password-protected. Ensure valid unencrypted PDFs are provided.
- **Empty Output Word Document**: Check if `pdf_proc.extract_text_from_pdf()` returned content. If the input PDF is scanned/image-only, standard text extraction will not extract text without an OCR engine.
- **Missing python-docx Styles**: Ensure default styles or standard fonts are used. The implementation safely adds custom run properties and alignments without external template dependencies.

---

## 12. Future Enhancements

- **Template-Based Document Generation**: Utilize Jinja-style placeholders (`{{placeholder}}`) inside pre-designed `.docx` templates for dynamic filling.
- **Advanced OCR Parsing**: Integrate OCR engines (e.g. Tesseract) to parse text from scanned image PDFs.
- **PDF Watermarking & Encryption**: Add watermarking and password-based encryption to generated PDFs using PyPDF2.
- **Batch Processing CLI**: Add command-line arguments (`argparse` / `click`) to batch process entire folders of documents.
