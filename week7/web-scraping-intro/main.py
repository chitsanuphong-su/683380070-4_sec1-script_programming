import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from scraper import AutomateBoringStuffScraper

def main():
    scraper = AutomateBoringStuffScraper()
    data = scraper.parse_table_of_contents()

    if data:
        print("\n==========================================")
        print(f" Page Title     : {data['page_title']}")
        print(f" Total Entries  : {data['total_chapters']}")
        print("==========================================\n")

        for idx, item in enumerate(data['chapters'], 1):
            print(f"[{idx:02d}] {item['title']}")
            print(f"     URL: {item['url']}")
        print("\n------------------------------------------")
    else:
        print("Failed to scrape data.")

if __name__ == "__main__":
    main()