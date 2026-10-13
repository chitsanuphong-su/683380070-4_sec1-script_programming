import os
import json
import datetime
from .utils import setup_logging, log_audit_entry, ensure_directory_exists, get_env_variable
from .email_tasks import EmailTasks
from .sms_tasks import SMSTasks
from .template_renderer import TemplateRenderer

logger = setup_logging(__name__)

class CommunicationAgent:
    """
    An agent that orchestrates communication tasks (email, SMS, inbox processing)
    based on a structured configuration file, managing an internal context for dynamic values.
    """

    def __init__(self, config, base_dir, dry_run=True, email_tasks=None, sms_tasks=None):
        self.config = config
        self.base_dir = base_dir
        self.dry_run = dry_run
        self.audit_log = []
        self.context = {}
        self.start_time = datetime.datetime.now()
        self.template_renderer = TemplateRenderer(dry_run=dry_run)

        # Track stats for summary
        self.task_stats = {
            "total_tasks": len(config.get("tasks", [])),
            "successful_tasks": 0,
            "failed_tasks": 0,
            "skipped_tasks": 0
        }

        # Initialize or inject communication task handlers
        if email_tasks is not None:
            self.email_tasks = email_tasks
        else:
            try:
                sender_email = get_env_variable("SENDER_EMAIL", default="dryrun_sender@example.com" if dry_run else None)
                sender_app_password = get_env_variable("SENDER_APP_PASSWORD", default="dummy_pass" if dry_run else None)
                smtp_server = get_env_variable("SMTP_SERVER", default="smtp.example.com" if dry_run else None)
                smtp_port = int(get_env_variable("SMTP_PORT", default="587" if dry_run else None))
                imap_server = get_env_variable("IMAP_SERVER", default="imap.example.com" if dry_run else None)

                self.email_tasks = EmailTasks(
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    imap_server=imap_server,
                    sender_email=sender_email,
                    sender_password=sender_app_password,
                    dry_run=dry_run
                )
            except ValueError as e:
                logger.critical(f"Agent initialization failed: Missing environment variables. {e}")
                raise

        if sms_tasks is not None:
            self.sms_tasks = sms_tasks
        else:
            self.sms_tasks = SMSTasks(self.email_tasks)

        logger.info(f"CommunicationAgent initialized (Dry-run: {self.dry_run}).")

    def _update_context(self, key, value):
        """Updates a value in the agent's context."""
        self.context[key] = value
        logger.debug(f"Context updated: '{key}' = {value}")

    def _get_context_value(self, key, default=None):
        """Retrieves a value from the agent's context."""
        return self.context.get(key, default)

    def _render_template(self, template_string):
        """Renders a template string using the current agent context."""
        try:
            return self.template_renderer.render(template_string, self.context)
        except Exception as e:
            log_audit_entry(
                self.audit_log,
                "ERROR",
                f"Template rendering failed: {e}",
                "template_render",
                {"template": str(template_string)}
            )
            raise

    def _process_task(self, task):
        """Dispatches a task to the appropriate handler and manages context."""
        task_type = task.get("type")
        task_name = task.get("name", task_type)
        task_params = task.get("parameters", {})
        output_context_key = task.get("output_context_key")

        logger.info(f"Executing task: '{task_name}' (Type: {task_type})")
        log_audit_entry(self.audit_log, "INFO", f"Starting task '{task_name}'", task_type, {"name": task_name})

        success = False
        task_output_data = None

        try:
            if task_type == "send_email":
                recipients = {}
                for k, v in task_params.get('recipients', {}).items():
                    recipients[k] = [self._render_template(r) for r in v]

                subject = self._render_template(task_params.get("subject_template"))
                body = self._render_template(task_params.get("body_template"))

                attachments = []
                for att_path in task_params.get("attachments", []):
                    # att_path can be a template or plain path
                    rendered_subpath = self._render_template(att_path)
                    full_att_path = os.path.join(self.base_dir, rendered_subpath)
                    attachments.append(full_att_path)

                is_html = task_params.get("is_html", False)
                success = self.email_tasks.send_email(recipients, subject, body, attachments, is_html)
                if success:
                    task_output_data = {
                        "recipients": recipients,
                        "subject": subject,
                        "attachments": attachments
                    }

            elif task_type == "send_sms":
                phone_numbers = [self._render_template(p) for p in task_params.get("phone_numbers", [])]
                message = self._render_template(task_params.get("message_template"))
                raw_carrier = task_params.get("carrier_name", "")
                carrier_name = self._render_template(raw_carrier) if raw_carrier else None

                success = self.sms_tasks.send_sms(phone_numbers, message, carrier_name)
                if success:
                    task_output_data = {
                        "phone_numbers": phone_numbers,
                        "message": message,
                        "carrier_name": carrier_name
                    }

            elif task_type == "process_inbox":
                mailbox = task_params.get("mailbox", "INBOX")
                search_criteria = task_params.get("search_criteria", {})
                rules = task_params.get("rules", [])
                download_rel = task_params.get("download_attachments_base_dir", "data/incoming_attachments")
                download_attachments_base_dir = os.path.join(self.base_dir, download_rel)

                rendered_sender = (
                    self._render_template(search_criteria.get("from_sender", ""))
                    if search_criteria.get("from_sender") else None
                )
                rendered_subject_contains = (
                    self._render_template(search_criteria.get("subject_contains", ""))
                    if search_criteria.get("subject_contains") else None
                )

                uids = self.email_tasks.search_emails(
                    mailbox=mailbox,
                    criteria=search_criteria.get("status", "UNSEEN"),
                    from_sender=rendered_sender,
                    subject_contains=rendered_subject_contains
                )

                processed_emails_summary = []
                all_actions_succeeded = True

                if uids:
                    for uid in uids:
                        email_info = self.email_tasks.fetch_email_content(
                            uid=uid,
                            mark_as_read=True,
                            download_attachments_dir=download_attachments_base_dir
                        )
                        if email_info:
                            processed_emails_summary.append(email_info)
                            # Evaluate rules for this email
                            for r_idx, rule in enumerate(rules):
                                if_conditions = rule.get("if", {})
                                then_actions = rule.get("then", {})

                                condition_met = True
                                if "subject_contains" in if_conditions:
                                    expected_sub = self._render_template(if_conditions["subject_contains"])
                                    if expected_sub.lower() not in email_info['subject'].lower():
                                        condition_met = False

                                if "body_contains" in if_conditions:
                                    expected_body = self._render_template(if_conditions["body_contains"])
                                    if expected_body.lower() not in email_info['text_body'].lower():
                                        condition_met = False

                                if "has_attachments" in if_conditions:
                                    if if_conditions["has_attachments"] != email_info['has_attachments']:
                                        condition_met = False

                                if "from_sender_is" in if_conditions:
                                    expected_sender = self._render_template(if_conditions["from_sender_is"])
                                    if expected_sender.lower() not in email_info['sender'].lower():
                                        condition_met = False

                                if condition_met:
                                    logger.info(f"Rule {r_idx+1} matched for email UID {email_info['uid']}. Applying actions...")
                                    rule_context = {**self.context, **email_info}

                                    # Action 1: send_sms_alert
                                    if then_actions.get("send_sms_alert"):
                                        alert_msg_template = then_actions.get(
                                            "alert_message_template",
                                            "Urgent email received: {subject} from {sender}"
                                        )
                                        alert_message = self.template_renderer.render(alert_msg_template, rule_context)
                                        raw_phones = then_actions.get("alert_phone_numbers", [])
                                        alert_phones = [self._render_template(p) for p in raw_phones]
                                        raw_c = then_actions.get("alert_carrier", "")
                                        alert_carrier = self._render_template(raw_c) if raw_c else None

                                        sms_res = self.sms_tasks.send_sms(alert_phones, alert_message, alert_carrier)
                                        if not sms_res:
                                            all_actions_succeeded = False
                                            log_audit_entry(self.audit_log, "WARNING", "SMS alert action failed in inbox rule.", task_type)

                                    # Action 2: reply_with_template
                                    if "reply_with_template" in then_actions:
                                        reply_body_template = then_actions["reply_with_template"]
                                        reply_subject_template = then_actions.get("reply_subject_template", "Re: {subject}")
                                        reply_body = self.template_renderer.render(reply_body_template, rule_context)
                                        reply_subject = self.template_renderer.render(reply_subject_template, rule_context)

                                        # Safeguard: Do not reply to empty or own auto-reply if already re-processed
                                        reply_target = email_info['sender']
                                        if reply_target and not email_info['subject'].startswith("Re: Re:"):
                                            reply_res = self.email_tasks.send_email(
                                                recipients={'to': [reply_target]},
                                                subject=reply_subject,
                                                body=reply_body
                                            )
                                            if not reply_res:
                                                all_actions_succeeded = False
                                                log_audit_entry(self.audit_log, "WARNING", "Auto-reply action failed in inbox rule.", task_type)
                                        else:
                                            logger.warning(f"Auto-reply loop detected or skipped for {email_info['subject']}.")
                                else:
                                    logger.info(f"Rule {r_idx+1} did not match email UID {email_info['uid']}.")
                        else:
                            all_actions_succeeded = False
                            logger.error(f"Failed to fetch content for email UID {uid}.")

                    success = all_actions_succeeded
                    task_output_data = {"processed_emails_count": len(processed_emails_summary), "emails": processed_emails_summary}
                else:
                    logger.info("No emails found matching search criteria for inbox processing.")
                    success = True
                    task_output_data = {"processed_emails_count": 0, "emails": []}
            else:
                log_audit_entry(self.audit_log, "WARNING", f"Unsupported task type: {task_type}", task_type)
                self.task_stats["skipped_tasks"] += 1
                return

            if success:
                self.task_stats["successful_tasks"] += 1
                if task_output_data is not None and output_context_key:
                    self._update_context(output_context_key, task_output_data)
                log_audit_entry(self.audit_log, "SUCCESS", f"Task '{task_name}' completed successfully.", task_type, {"name": task_name})
            else:
                self.task_stats["failed_tasks"] += 1
                log_audit_entry(self.audit_log, "ERROR", f"Task '{task_name}' failed.", task_type, {"name": task_name})

        except Exception as e:
            self.task_stats["failed_tasks"] += 1
            log_audit_entry(
                self.audit_log,
                "ERROR",
                f"An error occurred during task '{task_name}': {e}",
                task_type,
                {"error": str(e), "task_name": task_name}
            )
            logger.error(f"Error during task '{task_name}': {e}", exc_info=True)

    def _generate_audit_report(self, output_dir="reports"):
        """Generates a JSON audit report including execution summary and event logs."""
        ensure_directory_exists(output_dir)
        report_filename = f"audit_report_comm_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(output_dir, report_filename)

        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        final_status = "SUCCESS" if self.task_stats["failed_tasks"] == 0 else "PARTIAL_FAILURE"

        # Record completion in audit log before serialization
        log_audit_entry(
            self.audit_log,
            "INFO",
            f"Audit report generated at {report_path}",
            "audit_report",
            {
                "final_status": final_status,
                "duration_seconds": round(duration, 2),
                "stats": self.task_stats
            }
        )

        full_report_data = {
            "summary": {
                "generated_at": datetime.datetime.now().isoformat(),
                "execution_duration_seconds": round(duration, 2),
                "dry_run": self.dry_run,
                "final_status": final_status,
                "stats": self.task_stats
            },
            "events": self.audit_log
        }

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(full_report_data, f, indent=4, ensure_ascii=False)
            logger.info(f"Audit report saved to: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Failed to save audit report: {e}")
            raise

    def run(self):
        """Executes all tasks defined in the configuration."""
        logger.info(f"Starting Communication Agent run (Dry-run: {self.dry_run})...")
        log_audit_entry(self.audit_log, "INFO", "Communication Agent started.", "agent_run", {"dry_run": self.dry_run})

        # Pre-populate demonstration context as specified in PDF
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        self._update_context("report_name", "DailySalesSummary")
        self._update_context("report_date", today_str)
        self._update_context("sales_figure", 12345.67)
        self._update_context("total_customers", 500)
        self._update_context("attachment_path_1", "data/reports/sales_report.pdf")
        self._update_context("attachment_path_2", "data/reports/summary_data.xlsx")

        for task in self.config.get("tasks", []):
            self._process_task(task)

        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        log_audit_entry(
            self.audit_log,
            "INFO",
            f"Communication Agent finished in {duration:.2f} seconds.",
            "agent_run_summary",
            {"duration": round(duration, 2)}
        )
        logger.info(f"Communication Agent finished. Total time: {duration:.2f} seconds.")

        audit_report_dir = os.path.join(self.base_dir, 'reports')
        return self._generate_audit_report(audit_report_dir)
