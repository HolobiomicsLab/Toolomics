import os
import sys
import re
import time
import random
import tempfile
import markdownify
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
import helium
from helium import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Browser:
    def __init__(self, headless: bool = True):
        """Initialize the browser with Helium."""
        self.screenshot_folder = os.path.join(os.getcwd(), ".screenshots")
        self.headless = headless
        self._start_browser()
        
    def _start_browser(self):
        """Start the browser with appropriate options."""
        options = {
            'headless': self.headless,
        }
        start_chrome(**options)
        
    def go_to(self, url: str) -> bool:
        """Navigate to a specified URL."""
        try:
            go_to(url)
            time.sleep(random.uniform(0.5, 2.0))
            self.human_scroll()
            return True
        except Exception as e:
            return False

    def human_scroll(self):
        """Simulate human-like scrolling."""
        for _ in range(random.randint(1, 3)):
            scroll_pixels = random.randint(150, 600)
            get_driver().execute_script(f"window.scrollBy(0, {scroll_pixels});")
            time.sleep(random.uniform(0.5, 1.5))
            if random.random() < 0.3:
                get_driver().execute_script(f"window.scrollBy(0, -{random.randint(50, 200)});")
                time.sleep(random.uniform(0.3, 0.8))

    def is_sentence(self, text: str) -> bool:
        """Check if the text qualifies as a meaningful sentence."""
        text = text.strip()
        if any(c.isdigit() for c in text):
            return True
        words = re.findall(r'\w+', text, re.UNICODE)
        word_count = len(words)
        has_punctuation = any(text.endswith(p) for p in ['.', '，', ',', '!', '?', '。', '！', '？'])
        return word_count >= 5 and (has_punctuation or word_count > 4)

    def get_text(self) -> Optional[str]:
        """Get page text as formatted Markdown."""
        try:
            page_source = get_driver().page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            for element in soup(['script', 'style', 'noscript', 'meta', 'link']):
                element.decompose()
                
            markdown_converter = markdownify.MarkdownConverter(
                heading_style="ATX",
                strip=['a'],
                autolinks=False,
                bullets='•',
                strong_em_symbol='*',
                default_title=False,
            )
            
            markdown_text = markdown_converter.convert(str(soup.body))
            lines = []
            
            for line in markdown_text.splitlines():
                stripped = line.strip()
                if stripped and self.is_sentence(stripped):
                    cleaned = ' '.join(stripped.split())
                    lines.append(cleaned)
                    
            result = "[Start of page]\n\n" + "\n\n".join(lines) + "\n\n[End of page]"
            result = re.sub(r'!\[(.*?)\]\(.*?\)', r'[IMAGE: \1]', result)
            return result[:4096]
        except Exception:
            return None

    def clean_url(self, url: str) -> str:
        """Clean URL to keep only essential parts."""
        clean = url.split('#')[0]
        parts = clean.split('?', 1)
        base_url = parts[0]
        
        if len(parts) > 1:
            query = parts[1]
            essential_params = []
            for param in query.split('&'):
                if any(param.startswith(prefix) for prefix in ['q=', 's=', 'search=']):
                    essential_params.append(param)
            if essential_params:
                return f"{base_url}?{'&'.join(essential_params)}"
        return base_url

    def is_link_valid(self, url: str) -> bool:
        """Check if a URL is a valid navigable link."""
        if len(url) > 128:
            return False
            
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return False
            
        invalid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.ico', '.xml', '.json', '.pdf']
        return not any(url.lower().endswith(ext) for ext in invalid_extensions)

    def get_navigable(self) -> List[str]:
        """Get all navigable links on the current page."""
        try:
            links = []
            link_elements = find_all(Link())
            
            for element in link_elements:
                href = element.web_element.get_attribute("href")
                if href and href.startswith(("http", "https")) and self.is_link_valid(href):
                    links.append(self.clean_url(href))
                    
            return list(set(links))  # Remove duplicates
        except Exception:
            return []

    def get_current_url(self) -> str:
        """Get the current URL."""
        return get_driver().current_url

    def get_page_title(self) -> str:
        """Get the page title."""
        return get_driver().title

    def screenshot(self, filename: str = 'updated_screen.png') -> bool:
        """Take a screenshot."""
        try:
            if not os.path.exists(self.screenshot_folder):
                os.makedirs(self.screenshot_folder)
            path = os.path.join(self.screenshot_folder, filename)
            get_driver().save_screenshot(path)
            return True
        except Exception:
            return False

    def get_screenshot(self) -> str:
        """Get screenshot path."""
        return os.path.join(self.screenshot_folder, "updated_screen.png")

    def close(self):
        """Close the browser."""
        try:
            kill_browser()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage example:
if __name__ == "__main__":
    with Browser(headless=False) as browser:
        browser.go_to("https://www.google.com")
        browser.screenshot()
        text = browser.get_text()
        navigable_links = browser.get_navigable()
        print(f"Current URL: {browser.get_current_url()}")
        print(f"Page title: {browser.get_page_title()}")
        print(f"Page text: {text[:200]}...")
        print(f"Navigable links: {navigable_links[:5]}")
