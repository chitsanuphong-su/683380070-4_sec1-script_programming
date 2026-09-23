import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from config_parser import ConfigParser
from scraper_agent import ScraperAgent

def main():
    config_path = os.path.join(os.path.dirname(__file__), 'configs', 'example_site_config.json')
    config_parser = ConfigParser(config_path)
    config = config_parser.load_config()
    
    agent = ScraperAgent(config, browser='chrome', headless=True)
    agent.run()

if __name__ == "__main__":
    main()