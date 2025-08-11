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
from selenium.webdriver.chrome.options import Options as ChromeOptions
# Override helium's ChromeOptions with selenium's for better compatibility
helium.ChromeOptions = ChromeOptions

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Browser:
    def __init__(self, headless: bool = True):
        """Initialize the browser with Helium."""
        self.screenshot_folder = os.path.join(os.getcwd(), ".screenshots")
        self.headless = headless
        self._start_browser()
        
    def _start_browser(self):
        """Start the browser with appropriate options."""
        try:
            # Detect containerized environment
            in_container = os.environ.get('DISPLAY') == ':99' or os.path.exists('/.dockerenv')
            
            if in_container:
                # Container environment - use Chromium with optimized settings
                chrome_options = helium.ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-software-rasterizer')
                chrome_options.add_argument('--disable-background-timer-throttling')
                chrome_options.add_argument('--disable-renderer-backgrounding')
                chrome_options.add_argument('--disable-backgrounding-occluded-windows')
                chrome_options.add_argument('--disable-client-side-phishing-detection')
                chrome_options.add_argument('--disable-crash-reporter')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-features=TranslateUI')
                chrome_options.add_argument('--disable-ipc-flooding-protection')
                chrome_options.add_argument('--memory-pressure-off')
                chrome_options.add_argument('--max_old_space_size=4096')
                chrome_options.add_argument('--single-process')
                
                if self.headless:
                    chrome_options.add_argument('--headless=new')
                
                # Set Chromium binary path for container
                chrome_options.binary_location = '/usr/bin/chromium'
                
                # Start with custom options
                start_chrome(options=chrome_options)
                print("Started Chromium in container environment")
            else:
                # Desktop environment - try Chrome first, fallback to Chromium
                try:
                    options = {'headless': self.headless}
                    start_chrome(**options)
                    print("Started Chrome in desktop environment")
                except Exception as chrome_error:
                    print(f"Chrome not available, trying Chromium: {chrome_error}")
                    chrome_options = helium.ChromeOptions()
                    chrome_options.binary_location = '/usr/bin/chromium'
                    if self.headless:
                        chrome_options.add_argument('--headless=new')
                    start_chrome(options=chrome_options)
                    print("Started Chromium in desktop environment")
                
        except Exception as e:
            print(f"Failed to start browser with Helium: {e}")
            # Final fallback with minimal options
            try:
                chrome_options = helium.ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--single-process')
                # Try both Chrome and Chromium paths
                for browser_path in ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']:
                    if os.path.exists(browser_path):
                        chrome_options.binary_location = browser_path
                        break
                
                start_chrome(options=chrome_options)
                print("Successfully started browser with fallback options")
            except Exception as fallback_error:
                print(f"All browser initialization attempts failed: {fallback_error}")
                raise RuntimeError(f"Unable to initialize browser. Chrome/Chromium may not be installed or accessible: {fallback_error}")
        
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

    def is_link_valid(self, url: str) -> bool:
        """Check if a URL is a valid navigable link."""
        if not url or len(url) > 512:
            return False
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return False
            if parsed_url.scheme not in ['http', 'https']:
                return False
            path = parsed_url.path.lower()
            download_extensions = [
                '.pdf', '.mp4', '.mp3', '.avi', '.mov', '.wmv', '.flv', '.mkv',
                '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.zip', '.rar', '.gz', '.tar', '.7z', '.bz2',
                '.csv', '.json', '.xml', '.txt', '.log',
                '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg', '.webp',
                '.exe', '.dmg', '.pkg', '.deb', '.rpm', '.msi', '.apk',
                '.iso', '.img', '.bin'
            ]
            for ext in download_extensions:
                if path.endswith(ext):
                    return False
            return True
            
        except Exception as e:
            print(f"Error validating URL {url}: {e}")
            return False

    def get_navigable(self) -> List[str]:
        """Get all navigable links on the current page."""
        try:
            links = []
            link_elements = find_all(Link())
            
            for element in link_elements:
                href = element.web_element.get_attribute("href")
                if href and href.startswith(("http", "https")) and self.is_link_valid(href):
                    links.append(href)
                    
            return list(set(links))  # Remove duplicates
        except Exception:
            return []

    def _get_downloadable_extensions(self) -> List[str]:
        """Get list of downloadable file extensions."""
        return [
            '.pdf', '.mp4', '.mp3', '.avi', '.mov', '.wmv', '.flv', '.mkv',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.gz', '.tar', '.7z', '.bz2',
            '.csv', '.json', '.xml', '.txt', '.log',
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg', '.webp',
            '.exe', '.dmg', '.pkg', '.deb', '.rpm', '.msi', '.apk',
            '.iso', '.img', '.bin'
        ]

    def _convert_to_absolute_url(self, href: str, current_url: str, base_url: str) -> str:
        """Convert relative URL to absolute URL."""
        if href.startswith('/'):
            return base_url + href
        elif href.startswith('./') or not href.startswith(('http://', 'https://')):
            if href.startswith('./'):
                href = href[2:]
            current_path = '/'.join(current_url.split('/')[:-1])
            return f"{current_path}/{href}"
        else:
            return href

    def _is_downloadable_by_extension(self, url: str, extensions: List[str]) -> bool:
        """Check if URL has a downloadable file extension."""
        parsed_url = urlparse(url)
        path_lower = parsed_url.path.lower()
        return any(path_lower.endswith(ext) for ext in extensions)

    def _is_downloadable_by_pattern(self, url: str, patterns: List[str]) -> bool:
        """Check if URL matches download patterns."""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in patterns)

    def _is_downloadable_by_query(self, url: str, extensions: List[str]) -> bool:
        """Check if URL has downloadable indicators in query parameters."""
        parsed_url = urlparse(url)
        if not parsed_url.query:
            return False
        query_lower = parsed_url.query.lower()
        if any(param in query_lower for param in ['file=', 'filename=', 'download=', 'attachment=']):
            return True
        for param in parsed_url.query.split('&'):
            if '=' in param:
                value = param.split('=', 1)[1]
                if any(value.lower().endswith(ext) for ext in extensions):
                    return True
        return False

    def _extract_links_from_elements(self, current_url: str, base_url: str) -> List[str]:
        """Extract downloadable links from HTML elements."""
        links = []
        extensions = self._get_downloadable_extensions()
        
        try:
            link_elements = find_all(Link())
            for element in link_elements:
                href = element.web_element.get_attribute("href")
                if not href:
                    continue
                    
                full_url = self._convert_to_absolute_url(href, current_url, base_url)
                
                if (self._is_downloadable_by_extension(full_url, extensions) or
                    self._is_downloadable_by_query(full_url, extensions)):
                    links.append(full_url)
                    
        except Exception as e:
            print(f"Error extracting links from elements: {e}")
            
        return links

    def _extract_links_from_attributes(self, current_url: str, base_url: str) -> List[str]:
        """Extract downloadable links from HTML attributes like download, data-url, etc."""
        links = []
        extensions = self._get_downloadable_extensions()
        patterns = self._get_download_patterns()
        
        try:
            page_source = get_driver().page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find elements with download attributes
            download_elements = soup.find_all(['a', 'button'], attrs={'download': True})
            for elem in download_elements:
                href = elem.get('href')
                if href:
                    full_url = self._convert_to_absolute_url(href, current_url, base_url)
                    links.append(full_url)
            
            # Find elements with data-url or data-file attributes
            data_elements = soup.find_all(attrs={'data-url': True}) + soup.find_all(attrs={'data-file': True})
            for elem in data_elements:
                data_url = elem.get('data-url') or elem.get('data-file')
                if data_url:
                    full_url = self._convert_to_absolute_url(data_url, current_url, base_url)
                    
                    # Check if it looks like a downloadable file
                    if (self._is_downloadable_by_extension(full_url, extensions) or
                        self._is_downloadable_by_pattern(full_url, patterns)):
                        links.append(full_url)
                        
        except Exception as e:
            print(f"Error extracting links from attributes: {e}")
            
        return links

    def _deduplicate_links(self, links: List[str]) -> List[str]:
        """Remove duplicate links and clean URLs."""
        unique_links = []
        seen = set()
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        return unique_links

    def get_downloadable(self) -> List[str]:
        """Get all downloadable resource links on the current page."""
        try:
            current_url = self.get_current_url()
            base_url = f"{urlparse(current_url).scheme}://{urlparse(current_url).netloc}"
            all_links = []
            element_links = self._extract_links_from_elements(current_url, base_url)
            all_links.extend(element_links)
            attribute_links = self._extract_links_from_attributes(current_url, base_url)
            all_links.extend(attribute_links)
            return self._deduplicate_links(all_links)
            
        except Exception as e:
            print(f"Error getting downloadable links: {e}")
            return []

    def download_file(self, url: str) -> Optional[tuple[bool, str]]:
        """Download a file from URL to current directory.
        
        Args:
            url: The URL of file to download
            
        Returns:
            tuple[bool, str] | None: (success_status, filename) if successful, None on failure
        """
        try:
            import requests
            from urllib.parse import urlparse, unquote
            import os
            import re
            
            # Validate URL is downloadable
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return None
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            try:
                head_response = session.head(url, allow_redirects=True, timeout=10)
                final_url = head_response.url
            except:
                final_url = url
            
            response = session.get(url, stream=True, allow_redirects=True, timeout=30)
            response.raise_for_status()
            
            filename = None
            
            # 1. Try Content-Disposition header
            if 'content-disposition' in response.headers:
                cd = response.headers['content-disposition']
                filename_match = re.search(r'filename[*]?=([^;]+)', cd)
                if filename_match:
                    filename = filename_match.group(1).strip('"\'')
                    filename = unquote(filename)  # URL decode
            
            # 2. Try final URL after redirects
            if not filename:
                final_parsed = urlparse(response.url)
                filename = os.path.basename(final_parsed.path)
                if filename:
                    filename = unquote(filename)  # URL decode
            
            # 3. Try original URL
            if not filename:
                filename = os.path.basename(parsed.path)
                if filename:
                    filename = unquote(filename)  # URL decode
            
            # 4. Try to guess from Content-Type
            if not filename:
                content_type = response.headers.get('content-type', '').lower()
                extension_map = {
                    'application/pdf': '.pdf',
                    'application/msword': '.doc',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                    'application/vnd.ms-excel': '.xls',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
                    'application/zip': '.zip',
                    'text/csv': '.csv',
                    'application/json': '.json',
                    'text/plain': '.txt',
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'video/mp4': '.mp4',
                    'audio/mpeg': '.mp3',
                }
                
                for mime_type, ext in extension_map.items():
                    if mime_type in content_type:
                        filename = f"downloaded_file_{int(time.time())}{ext}"
                        break
            
            # 5. Final fallback
            if not filename or filename == '/':
                filename = f"downloaded_file_{int(time.time())}"
            
            # Clean filename - remove invalid characters
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filename = filename.strip()
            
            # Ensure we don't overwrite existing files
            original_filename = filename
            counter = 1
            while os.path.exists(filename):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                counter += 1
            
            # Save to current directory
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Successfully downloaded: {filename} ({os.path.getsize(filename)} bytes)")
            return (True, filename)
            
        except Exception as e:
            print(f"Error downloading file from {url}: {e}")
            return None

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

    def is_session_valid(self) -> bool:
        """Check if the browser session is still valid."""
        try:
            # Try to get current URL to test if session is alive
            current_url = get_driver().current_url
            return current_url is not None
        except Exception:
            return False

    def quit(self):
        """Quit the browser session."""
        try:
            kill_browser()
        except Exception:
            pass

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
