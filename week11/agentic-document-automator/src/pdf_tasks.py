# agentic-document-automator/src/pdf_tasks.py
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import io
import os
try:
    from .utils import setup_logging, ensure_directory_exists
except ImportError:
    from utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


class PDFTasks:
    """
    Handles advanced PDF operations for the Document Agent.
    """

    def __init__(self):
        logger.info("PDFTasks initialized.")

    def _create_text_watermark_pdf(self, watermark_text, temp_pdf_path="temp_watermark.pdf",
                                   font_size=50, color=(0, 0, 0, 0.2), angle=45, page_size=None):
        """
        Creates a single-page PDF with a text watermark using ReportLab.
        This PDF can then be overlaid onto other PDFs.
        Returns the path to the generated temporary watermark PDF.
        """
        buffer = io.BytesIO()
        if page_size:
            width, height = page_size
        else:
            from reportlab.lib.pagesizes import A4
            width, height = A4

        c = canvas.Canvas(buffer, pagesize=(width, height))

        # Handle color and opacity (r, g, b, alpha)
        if len(color) == 4:
            r, g, b, a = color
        elif len(color) == 3:
            r, g, b = color
            a = 0.2
        else:
            r, g, b, a = 0.5, 0.5, 0.5, 0.2

        c.setFillColor(Color(r, g, b, alpha=a))
        c.setFont('Helvetica-Bold', font_size)
        c.translate(width / 2.0, height / 2.0)
        c.rotate(angle)

        text_width = c.stringWidth(watermark_text, 'Helvetica-Bold', font_size)
        c.drawString(-text_width / 2.0, -font_size / 4.0, watermark_text)

        c.showPage()
        c.save()

        buffer.seek(0)
        ensure_directory_exists(os.path.dirname(temp_pdf_path))
        with open(temp_pdf_path, 'wb') as f:
            f.write(buffer.getvalue())

        logger.info(f"Generated temporary watermark PDF: {temp_pdf_path}")
        return temp_pdf_path

    def apply_watermark(self, input_pdf_path, output_pdf_path, watermark_text,
                        font_size=50, color=(0.5, 0.5, 0.5, 0.2), angle=45):
        """
        Applies a text watermark to each page of an input PDF and saves it.
        Adapts dynamically to the source page dimensions.
        """
        if not os.path.exists(input_pdf_path):
            logger.error(f"Input PDF for watermarking not found: {input_pdf_path}")
            return False

        output_dir = os.path.dirname(output_pdf_path)
        ensure_directory_exists(output_dir)
        temp_watermark_pdf = os.path.join(output_dir if output_dir else ".", "temp_text_watermark.pdf")

        try:
            reader = PdfReader(input_pdf_path)
            if len(reader.pages) == 0:
                logger.error(f"Input PDF '{input_pdf_path}' has no pages.")
                return False

            first_page = reader.pages[0]
            page_width = float(first_page.mediabox.width)
            page_height = float(first_page.mediabox.height)

            # Generate watermark overlay tailored to page dimensions
            self._create_text_watermark_pdf(
                watermark_text,
                temp_pdf_path=temp_watermark_pdf,
                font_size=font_size,
                color=color,
                angle=angle,
                page_size=(page_width, page_height)
            )

            watermark_reader = PdfReader(temp_watermark_pdf)
            watermark_page = watermark_reader.pages[0]

            writer = PdfWriter()
            for page in reader.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)

            with open(output_pdf_path, 'wb') as f:
                writer.write(f)

            logger.info(f"Watermark applied to '{input_pdf_path}'. Output saved to '{output_pdf_path}'.")
            return True
        except ImportError:
            logger.error("ReportLab is required for dynamic watermark generation. Please install it: pip install ReportLab")
            return False
        except Exception as e:
            logger.error(f"Error applying watermark to '{input_pdf_path}': {e}")
            return False
        finally:
            if os.path.exists(temp_watermark_pdf):
                try:
                    os.remove(temp_watermark_pdf)
                    logger.debug(f"Removed temporary watermark file: {temp_watermark_pdf}")
                except Exception as e:
                    logger.warning(f"Could not remove temporary watermark file: {e}")

    def merge_pdfs(self, pdf_paths, output_path):
        """
        Merges multiple PDF files into a single output PDF.
        """
        if not pdf_paths:
            logger.warning("No PDF paths provided for merging.")
            return False

        writer = PdfWriter()
        ensure_directory_exists(os.path.dirname(output_path))

        logger.info(f"Merging PDFs into '{output_path}'...")
        added_count = 0
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                logger.warning(f"Skipping non-existent PDF for merging: {pdf_path}")
                continue
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
                added_count += 1
                logger.info(f"Added '{pdf_path}' to merge queue.")
            except Exception as e:
                logger.error(f"Error reading PDF '{pdf_path}' for merging: {e}")
                continue

        if len(writer.pages) == 0:
            logger.warning("No pages were added to the merged PDF. Output file will be empty or not created.")
            return False

        try:
            with open(output_path, 'wb') as f:
                writer.write(f)
            logger.info(f"PDFs successfully merged to '{output_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error writing merged PDF to '{output_path}': {e}")
            return False

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts all text from a given PDF file.
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None

        text_content = ""
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            logger.info(f"Extracting text from '{pdf_path}' ({num_pages} pages)...")
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n--- Page End ---\n"
                else:
                    text_content += f"[Page {page_num + 1} has no text]\n--- Page End ---\n"
            logger.info(f"Successfully extracted text from '{pdf_path}'.")
            return text_content
        except Exception as e:
            logger.error(f"Error extracting text from '{pdf_path}': {e}")
            return None
