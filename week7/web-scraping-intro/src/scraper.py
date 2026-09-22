import requests
from bs4 import BeautifulSoup

class AutomateBoringStuffScraper:
    """Scraper tailored to the Automate the Boring Stuff 2nd Edition structure."""
    
    def __init__(self, target_url="https://automatetheboringstuff.com/2e/"):
        self.target_url = target_url

    def fetch_html(self):
        """Downloads HTML content using standard browser headers."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            response = requests.get(self.target_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def parse_table_of_contents(self, html_content=None):
        """Parses the page title, edition note, and Table of Contents links."""
        if html_content is None:
            html_content = self.fetch_html()
            if not html_content:
                return None

        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. Extract Page Title (e.g., "2nd Edition")
        h1_tag = soup.find('h1')
        title = h1_tag.get_text(strip=True) if h1_tag else "Title Not Found"

        # 2. Extract Table of Contents links
        toc_items = []
        content_body = soup.find('div', class_='content-body')
        
        if content_body:
            # Targets all chapter/appendix links inside the content-body list
            links = content_body.select('ul li a')
            for link in links:
                chapter_title = link.get_text(strip=True)
                relative_url = link.get('href', '')
                full_url = f"https://automatetheboringstuff.com{relative_url}" if relative_url.startswith('/') else relative_url
                
                toc_items.append({
                    "title": chapter_title,
                    "url": full_url
                })

        return {
            "page_title": title,
            "total_chapters": len(toc_items),
            "chapters": toc_items
        }