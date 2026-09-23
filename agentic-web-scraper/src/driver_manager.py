from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class DriverManager:
    def __init__(self, browser_name='chrome', headless=True):
        self.browser_name = browser_name.lower()
        self.headless = headless
        self.driver = None

    def get_driver(self):
        if self.driver:
            return self.driver
        
        if self.browser_name == 'chrome':
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--log-level=3')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            return self.driver
        else:
            raise ValueError(f"Unsupported browser: {self.browser_name}")

    def quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None