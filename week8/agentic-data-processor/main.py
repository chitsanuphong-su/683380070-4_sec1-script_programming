import os
from src.config_parser import ConfigParser
from src.data_agent import DataAgent
from src.utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(base_dir, 'configs', 'data_pipeline_config.json')

    try:
        ensure_directory_exists(os.path.join(base_dir, 'data'))
        ensure_directory_exists(os.path.join(base_dir, 'configs'))
        ensure_directory_exists(os.path.join(base_dir, 'reports'))

        config_parser = ConfigParser(config_file_path)
        config = config_parser.load_config()

        for task in config['tasks']:
            if 'file_path' in task:
                task['file_path'] = os.path.join(base_dir, task['file_path'])

        agent = DataAgent(config)
        agent.run()
        logger.info("Data processing completed successfully.")

    except Exception as e:
        logger.critical(f"Critical execution error: {e}", exc_info=True)

if __name__ == "__main__":
    main()