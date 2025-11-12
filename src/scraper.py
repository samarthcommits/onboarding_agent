import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class FullPageScraper:
    def __init__(self, url):
        chrome_options = Options()
        # Remove headless mode so the browser opens visibly
        # chrome_options.add_argument("--headless")  # Commented out for visibility
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.get(url)
        time.sleep(3)  # Allow initial load

        self.visited_links = set()
        self.visited_links.add(url)  # Mark the start page as visited

        self.scraped_data = {}  # Dictionary to store URL: Text

        # JSON file to store scraped data
        self.file_name = "scraped_data_from_pal.json"
        if os.path.exists(self.file_name):
            os.remove(self.file_name)  # Clear the file if it exists

    def extract_text(self, page_url):
        """Extract text from the current page and store it in JSON format."""
        text = self.driver.execute_script("return document.body.innerText").strip()

        if text and page_url not in self.scraped_data:
            self.scraped_data[page_url] = text  # Store text under the URL key
            with open(self.file_name, "w", encoding="utf-8") as f:
                json.dump(self.scraped_data, f, ensure_ascii=False, indent=4)  # Save to file
            print(f"Text Saved for: {page_url}")

    def explore_page(self, page_url):
        """Explore the page and extract text."""
        self.extract_text(page_url)  # Extract text before interacting

        # Scroll to reveal hidden content
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        self.extract_text(page_url)  # Extract text again after scrolling

    def click_links(self):
        """Find and visit all links recursively while handling stale elements."""
        while True:
            links = self.driver.find_elements(By.TAG_NAME, "a")  # Refresh elements

            for i in range(len(links)):  # Iterate over index, not element reference
                try:
                    links = self.driver.find_elements(By.TAG_NAME, "a")  # Refresh elements
                    link = links[i]  # Get updated element

                    href = link.get_attribute("href")
                    if href and href.startswith("http") and href not in self.visited_links:
                        self.visited_links.add(href)
                        print(f"Visiting: {href}")

                        self.driver.get(href)  # Navigate to new page
                        time.sleep(3)
                        self.explore_page(href)  # Scrape the new page

                        self.driver.back()  # Return to the previous page
                        time.sleep(2)
                except Exception as e:
                    print(f"Skipping broken link: {str(e)}")

    def start(self):
        """Begin the scraping process."""
        self.explore_page(self.driver.current_url)
        self.click_links()
        print("\n🎉 Scraping Complete! Data saved in 'scraped_data.json'.")

    def close(self):
        """Close the browser."""
        self.driver.quit()

# Run the scraper
# url = "https://pal.tech"  # Change to your target website
# scraper = FullPageScraper(url)
# scraper.start()
# scraper.close()
