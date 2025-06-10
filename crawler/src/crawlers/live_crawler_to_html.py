# scrape web with javascript
from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--html_in', type=str, help='The HTML link to crawl')
parser.add_argument('--html_out', type=str, default='savings.html', help='The HTML file to generate')
args = parser.parse_args()

# Configure ChromeDriver (Selenium >=4.10 expects Service / Options objects)
chrome_service = Service('./chromedriver-mac-arm64/chromedriver')
chrome_options = Options()
chrome_options.add_argument("--disable-features=NetworkServiceInProcess")
chrome_options.add_argument("--disable-http2")                  # bypass Akamai glitch
# Uncomment the next line to run head‑less in CI
# chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
driver.get(args.html_in)
time.sleep(8)
htmlSource = driver.page_source
# print(htmlSource)
print(f"Generating output file {args.html_out}")
f = open(args.html_out, "w")
f.write(htmlSource)
f.close()
