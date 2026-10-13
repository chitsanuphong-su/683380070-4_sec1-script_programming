import sys
import os
import argparse

# Add project root to Python path so src package is recognized
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.config_parser import ConfigParser
from src.communication_agent import CommunicationAgent
from src.utils import setup_logging, ensure_directory_exists, get_env_variable

logger = setup_logging(__name__)

def check_required_files(config, base_dir):
    """
    Checks if all required input attachment files specified in the config exist.
    """
    missing_files = []
    for task in config.get('tasks', []):
        if task.get('type') == 'send_email':
            attachments = task.get('parameters', {}).get('attachments', [])
            for att_path_template in attachments:
                # Literal pre-check if without formatting brackets or simple path
                clean_path = att_path_template
                if '{' in clean_path and '}' in clean_path:
                    # In actual run, context resolves dynamic attachment paths
                    continue
                file_path = os.path.join(base_dir, clean_path)
                if not os.path.exists(file_path):
                    missing_files.append(file_path)

    if missing_files:
        return False, missing_files
    return True, []

def main():
    """
    Main entry point for Agentic Communication Automator.
    Loads config, performs safety checks, and executes workflow.
    Defaults to safe offline dry-run mode unless --live is explicitly passed.
    """
    parser = argparse.ArgumentParser(description="Agentic Communication Workflows (Advanced Email & SMS)")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute live communication tasks against real SMTP/IMAP servers. (Requires explicit authorization)"
    )
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(base_dir, 'configs', 'comm_pipeline_config.json')

    try:
        # Ensure standard directories exist
        ensure_directory_exists(os.path.join(base_dir, 'data'))
        ensure_directory_exists(os.path.join(base_dir, 'data', 'reports'))
        ensure_directory_exists(os.path.join(base_dir, 'data', 'attachments'))
        ensure_directory_exists(os.path.join(base_dir, 'data', 'incoming_attachments'))
        ensure_directory_exists(os.path.join(base_dir, 'configs'))
        ensure_directory_exists(os.path.join(base_dir, 'reports'))

        logger.info(f"Loading configuration from: {config_file_path}")
        config_parser = ConfigParser(config_file_path)
        config = config_parser.load_config()

        # Check for required sample attachment files
        files_exist, missing = check_required_files(config, base_dir)
        if not files_exist:
            logger.critical(f"One or more required attachment files are missing: {', '.join(missing)}")
            sys.exit(1)

        dry_run = not args.live
        if dry_run:
            logger.info("=======================================================")
            logger.info("RUNNING IN DRY-RUN MODE (Safe offline simulation)")
            logger.info("No actual emails, SMS, or IMAP operations will be sent.")
            logger.info("Use --live flag only with explicit authorization.")
            logger.info("=======================================================")
        else:
            logger.warning("=======================================================")
            logger.warning("RUNNING IN LIVE MODE")
            logger.warning("Connecting to remote SMTP and IMAP servers...")
            logger.warning("=======================================================")

        logger.info("Initializing Communication Agent...")
        agent = CommunicationAgent(config=config, base_dir=base_dir, dry_run=dry_run)

        logger.info("Running Communication Agent workflow...")
        report_path = agent.run()

        logger.info(f"Communication automation workflow completed successfully. Audit report: {report_path}")

    except FileNotFoundError as e:
        logger.critical(f"File system error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.critical(f"Configuration or environment variable error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred during execution: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
