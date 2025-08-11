#!/usr/bin/env python3

import os
import subprocess
import sys

print("=== Browser Debug Information ===")

# Check if we're in a container
print(f"Container check:")
print(f"  /.dockerenv exists: {os.path.exists('/.dockerenv')}")
print(f"  DISPLAY env: {os.environ.get('DISPLAY', 'Not set')}")

# Check for browser binaries
browsers = [
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable', 
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/chrome'
]

print(f"\nBrowser binaries:")
for browser in browsers:
    exists = os.path.exists(browser)
    print(f"  {browser}: {'✓' if exists else '✗'}")
    if exists:
        try:
            result = subprocess.run([browser, '--version'], capture_output=True, text=True, timeout=5)
            print(f"    Version: {result.stdout.strip()}")
        except:
            print(f"    Version: Could not determine")

# Check for webdrivers
drivers = [
    '/usr/bin/chromedriver',
    '/usr/bin/chromium-driver',
    '/usr/local/bin/chromedriver'
]

print(f"\nWebDriver binaries:")
for driver in drivers:
    exists = os.path.exists(driver)
    print(f"  {driver}: {'✓' if exists else '✗'}")
    if exists:
        try:
            result = subprocess.run([driver, '--version'], capture_output=True, text=True, timeout=5)
            print(f"    Version: {result.stdout.strip()}")
        except:
            print(f"    Version: Could not determine")

# Check PATH
print(f"\nPATH environment variable:")
path_dirs = os.environ.get('PATH', '').split(':')
for i, path_dir in enumerate(path_dirs):
    print(f"  {i+1}. {path_dir}")

# Try to find chromedriver in PATH
print(f"\nSearching for chromedriver in PATH:")
try:
    result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  Found: {result.stdout.strip()}")
    else:
        print(f"  Not found in PATH")
except:
    print(f"  Error searching PATH")

# Test Selenium WebDriver import
print(f"\nTesting Selenium imports:")
try:
    from selenium import webdriver
    print("  selenium.webdriver: ✓")
    
    from selenium.webdriver.chrome.options import Options
    print("  selenium Chrome Options: ✓")
    
    from selenium.webdriver.chrome.service import Service
    print("  selenium Chrome Service: ✓")
    
except ImportError as e:
    print(f"  Import error: {e}")

# Test basic ChromeDriver instantiation
print(f"\nTesting ChromeDriver instantiation:")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Try different driver paths
    for driver_path in [None, '/usr/bin/chromedriver', '/usr/bin/chromium-driver']:
        try:
            if driver_path:
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)
            
            print(f"  ChromeDriver {'(auto-detect)' if not driver_path else f'({driver_path})'}: ✓")
            driver.quit()
            break
        except Exception as e:
            print(f"  ChromeDriver {'(auto-detect)' if not driver_path else f'({driver_path})'}: ✗ - {str(e)[:100]}")

except Exception as e:
    print(f"  Overall test failed: {e}")

print("\n=== End Debug Information ===")