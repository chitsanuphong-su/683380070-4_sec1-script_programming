import re
import string
import os
from .utils import setup_logging

logger = setup_logging(__name__)

# Allowed non-secret environment variables for ${ENV_VAR} syntax
ALLOWED_ENV_VARS = {
    "SENDER_EMAIL",
    "TEST_RECIPIENT_EMAIL",
    "TEST_SMS_PHONE_NUMBER",
    "TEST_SMS_CARRIER",
    "SMTP_SERVER",
    "SMTP_PORT",
    "IMAP_SERVER"
}

class TemplateRenderer:
    """
    Renders string templates using both context placeholders {key} and
    environment variable placeholders ${ENV_VAR}.
    Supports nested access like {attachments_meta.0.filepath} and numeric formatting like {sales_figure:.2f}.
    """

    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.default_fallbacks = {
            "SENDER_EMAIL": "dryrun_sender@example.com",
            "TEST_RECIPIENT_EMAIL": "dryrun_recipient@example.com",
            "TEST_SMS_PHONE_NUMBER": "1234567890",
            "TEST_SMS_CARRIER": "att",
            "SMTP_SERVER": "smtp.example.com",
            "SMTP_PORT": "587",
            "IMAP_SERVER": "imap.example.com",
        }
        logger.debug(f"TemplateRenderer initialized (dry_run={dry_run}).")

    def _resolve_nested_key(self, key_path, context):
        """
        Safely resolves nested keys such as 'attachments_meta.0.filepath'
        from dicts and lists without executing arbitrary code.
        """
        parts = key_path.split('.')
        current = context
        for part in parts:
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    raise KeyError(f"Key '{part}' not found in dict")
            elif isinstance(current, (list, tuple)):
                if part.isdigit():
                    idx = int(part)
                    if 0 <= idx < len(current):
                        current = current[idx]
                    else:
                        raise KeyError(f"Index {idx} out of range in list")
                else:
                    raise KeyError(f"Invalid list index '{part}'")
            else:
                raise KeyError(f"Cannot traverse into non-container type '{type(current).__name__}'")
        return current

    def render(self, template_string, context):
        """
        Renders a template string using context and allowed environment variables.
        Raises ValueError if required context keys or environment variables are missing or forbidden.
        """
        if template_string is None:
            return ""

        if not isinstance(template_string, str):
            template_string = str(template_string)

        # 1. First resolve environment variable placeholders: ${VAR_NAME}
        def replace_env(match):
            var_name = match.group(1)
            if var_name not in ALLOWED_ENV_VARS:
                raise ValueError(
                    f"Access to environment variable '${{{var_name}}}' is not permitted or restricted for security."
                )
            env_val = os.getenv(var_name)
            if env_val is None:
                if self.dry_run and var_name in self.default_fallbacks:
                    env_val = self.default_fallbacks[var_name]
                else:
                    raise ValueError(f"Required environment variable '{var_name}' is not set.")
            return str(env_val)

        rendered_str = re.sub(r'\$\{([A-Za-z0-9_]+)\}', replace_env, template_string)

        # 2. Resolve context placeholders: {path.to.key} or {path.to.key:format_spec}
        # We find tokens like {foo} or {foo.bar:spec}
        def replace_context(match):
            raw_token = match.group(1)
            # Check if there is format specifier e.g. sales_figure:.2f
            if ':' in raw_token:
                key_expr, format_spec = raw_token.split(':', 1)
            else:
                key_expr, format_spec = raw_token, None

            # Resolve key_expr from context
            try:
                if '.' in key_expr:
                    val = self._resolve_nested_key(key_expr, context)
                else:
                    if key_expr not in context:
                        raise KeyError(key_expr)
                    val = context[key_expr]

                if format_spec:
                    return format(val, format_spec)
                return str(val)
            except KeyError as e:
                logger.error(f"Missing context key '{key_expr}': {e}. Template: '{template_string}'")
                raise ValueError(f"Missing context key: {key_expr}")
            except Exception as e:
                logger.error(f"Formatting error for '{raw_token}': {e}")
                raise ValueError(f"Error formatting placeholder '{raw_token}': {e}")

        # Regex for matching context placeholders {key} or {key:format}
        # Avoid matching double brackets or already processed expressions
        pattern = r'\{([A-Za-z0-9_.]+?(?::[^{}]+)?)\}'
        try:
            rendered_str = re.sub(pattern, replace_context, rendered_str)
        except Exception as e:
            raise

        return rendered_str
