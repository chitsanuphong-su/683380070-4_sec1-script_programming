# agentic-document-automator/src/document_agent.py
import json
import datetime
try:
    from .utils import setup_logging, log_audit_entry, ensure_directory_exists
    from .pdf_tasks import PDFTasks
    from .word_tasks import WordTasks
except ImportError:
    from utils import setup_logging, log_audit_entry, ensure_directory_exists
    from pdf_tasks import PDFTasks
    from word_tasks import WordTasks

logger = setup_logging(__name__)


class DocumentAgent:
    """
    An agent that processes documents (PDF, Word) based on a
    structured configuration file.
    """

    def __init__(self, config):
        self.config = config
        self.audit_log = []
        self.start_time = datetime.datetime.now()
        self.pdf_processor = PDFTasks()
        self.word_processor = WordTasks()
        logger.info("Document Agent initialized with configuration.")

    def _process_task(self, task):
        """Dispatches a task to the appropriate processor."""
        task_type = task.get("type")
        task_name = task.get("name", task_type)
        logger.info(f"Executing task: '{task_name}' (Type: {task_type})")
        log_audit_entry(self.audit_log, "INFO", f"Starting task '{task_name}'", task_type, task)

        try:
            success = False
            if task_type == "generate_word_report":
                template_path = task.get("template_path")
                output_path = task.get("output_path")
                raw_placeholders = {**self.config.get("global_data", {}), **task.get("data", {})}
                # Ensure placeholder keys are formatted with {{...}}
                placeholders = {}
                for k, v in raw_placeholders.items():
                    if k.startswith("{{") and k.endswith("}}"):
                        placeholders[k] = v
                    else:
                        placeholders[f"{{{{{k}}}}}"] = v
                table_data = task.get("table_data")
                success = self.word_processor.generate_report_from_template(
                    template_path, output_path, placeholders, table_data
                )
            elif task_type == "apply_pdf_watermark":
                input_pdf = task.get("input_pdf")
                output_pdf = task.get("output_pdf")
                watermark_text = task.get("watermark_text")
                font_size = task.get("font_size", 50)
                color = task.get("color", [0.5, 0.5, 0.5, 0.2])
                angle = task.get("angle", 45)
                success = self.pdf_processor.apply_watermark(
                    input_pdf, output_pdf, watermark_text, font_size, tuple(color), angle
                )
            elif task_type == "merge_pdfs":
                input_pdfs = task.get("input_pdfs")
                output_pdf = task.get("output_pdf")
                success = self.pdf_processor.merge_pdfs(input_pdfs, output_pdf)
            elif task_type == "extract_pdf_text":
                input_pdf = task.get("input_pdf")
                output_text_file = task.get("output_text_file")
                extracted_text = self.pdf_processor.extract_text_from_pdf(input_pdf)
                if extracted_text is not None:
                    import os
                    ensure_directory_exists(os.path.dirname(output_text_file))
                    with open(output_text_file, 'w', encoding='utf-8') as f:
                        f.write(extracted_text)
                    success = True
                    logger.info(f"Extracted PDF text saved to {output_text_file}")
                else:
                    success = False
            elif task_type == "extract_word_text":
                input_docx = task.get("input_docx")
                output_text_file = task.get("output_text_file")
                extracted_text = self.word_processor.extract_text_from_word(input_docx)
                if extracted_text is not None:
                    import os
                    ensure_directory_exists(os.path.dirname(output_text_file))
                    with open(output_text_file, 'w', encoding='utf-8') as f:
                        f.write(extracted_text)
                    success = True
                    logger.info(f"Extracted Word text saved to {output_text_file}")
                else:
                    success = False
            else:
                log_audit_entry(self.audit_log, "WARNING", f"Unsupported task type: {task_type}", task_type, task)
                logger.warning(f"Unsupported task type: {task_type}")
                return False

            if success:
                log_audit_entry(self.audit_log, "SUCCESS", f"Task '{task_name}' completed successfully.", task_type, task)
            else:
                log_audit_entry(self.audit_log, "ERROR", f"Task '{task_name}' failed.", task_type, task)
            return success

        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"An error occurred during task '{task_name}': {e}",
                            task_type, {"error": str(e), "task_details": task})
            logger.error(f"Error during task '{task_name}': {e}", exc_info=True)
            return False

    def _generate_audit_report(self, output_dir="documents"):
        """Generates a JSON audit report."""
        import os
        ensure_directory_exists(output_dir)
        report_filename = f"audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(output_dir, report_filename)

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, indent=4, ensure_ascii=False)
            logger.info(f"Audit report saved to: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Failed to save audit report: {e}")
            log_audit_entry(self.audit_log, "CRITICAL", f"Failed to save audit report: {e}", "audit_report")
            return None

    def run(self):
        """Executes all tasks defined in the configuration."""
        logger.info("Starting Document Agent run...")
        log_audit_entry(self.audit_log, "INFO", "Document Agent started.", "agent_run")

        all_successful = True
        for task in self.config.get("tasks", []):
            task_success = self._process_task(task)
            if not task_success:
                all_successful = False

        end_time = datetime.datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        log_audit_entry(self.audit_log, "INFO", f"Document Agent finished in {duration:.2f} seconds. All success: {all_successful}", "agent_run_summary")
        logger.info(f"Document Agent finished. Total time: {duration:.2f} seconds.")

        # Determine report folder
        import os
        report_dir = "documents/reports"
        if "output_files" in self.config and "generated_report" in self.config["output_files"]:
            gen_dir = os.path.dirname(self.config["output_files"]["generated_report"])
            report_dir = os.path.join(gen_dir, "reports")

        self._generate_audit_report(report_dir)
        return all_successful
