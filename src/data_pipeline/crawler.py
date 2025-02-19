"""WebScraper class to scrape webpages and save content to JSON files."""

from typing import List, Optional
import json
import re
import requests
import bs4
from loguru import logger
from datetime import datetime
import time
import random
from tqdm import tqdm
import os


class BaseScraper:
    """Base class for web scraping."""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Initialize WebScraper with base URL and allowed domain."""
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.trusted_url = "https://www.gov.sg/trusted-sites"

    def get_page_content(self, url: str) -> Optional[bs4.BeautifulSoup]:
        """Fetch and parse webpage content.

        Args:
            url: URL of the webpage to fetch

        Returns:
            BeautifulSoup object of the webpage content
        """
        try:
            # Add sleep before making request
            time.sleep(random.uniform(self.min_delay, self.max_delay))

            headers = requests.utils.default_headers()
            headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
                }
            )
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return bs4.BeautifulSoup(response.text, "html.parser")

        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def extract_tbody_links(self) -> List[str]:
        """Extract all links from tbody tags.

        Returns:
            List of links extracted from tbody tags
        """
        soup = self.get_page_content(self.trusted_url)
        if not soup:
            logger.error("Failed to fetch trusted sites page")
            return []

        links = []
        # Find all tbody tags
        tbody_tags = soup.find_all("tbody")

        for tbody in tbody_tags:
            # Find all anchor tags within each tbody
            anchors = tbody.find_all("a")
            for anchor in anchors:
                href = anchor.get("href")
                if href:
                    links.append(href)
                    logger.debug(f"Found link in tbody: {href}")

        logger.info(f"Found {len(links)} links in tbody tags")
        return links


class WebScraper(BaseScraper):
    """WebScraper class to scrape webpages and save content to JSON files."""

    def __init__(
        self,
        base_url: str,
        allowed_domain: str,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
    ):
        """Initialize WebScraper with base URL and allowed domain.

        Args:
            base_url: Base URL to start scraping
            allowed_domain: Allowed domain to scrape
            min_delay: Minimum delay between requests
            max_delay: Maximum delay between requests
        """
        super().__init__(min_delay, max_delay)
        self.base_url = base_url
        self.allowed_domain = allowed_domain
        self.links_to_visit = set()  # Initialize empty set for links
        self.visited_links = set()  # Make sure this is initialized too
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Initialized WebScraper for {self.base_url}")
        logger.info(f"Allowed domain: {self.allowed_domain}")

    def save_content(self, link: str, content: str) -> None:
        """Save scraped content to JSON file.

        Args:
            link: URL of the page
            content: Cleaned text content of the page
        """
        try:
            file_path = f"data/{"".join([x if x.isalnum() else "_" for x in self.allowed_domain])}_{self.timestamp}.json"

            # Create initial file with empty array if it doesn't exist
            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w") as f:
                    f.write("[\n")

            # Append the new content with proper JSON formatting
            with open(file_path, "a") as f:
                # Add comma if not first entry
                if os.path.getsize(file_path) > 2:  # More than just "[\n"
                    f.write(",\n")

                json.dump(
                    {"link": link, "text": content}, f, ensure_ascii=False, indent=2
                )
                logger.debug(f"Saved cleaned content for: {link}")

        except IOError as e:
            logger.error(f"Failed to save data for {link}: {e}")

    def __del__(self):
        """Destructor to close the JSON array when scraping is complete."""
        try:
            file_path = f"data/data_{self.timestamp}.json"
            if os.path.exists(file_path):
                with open(file_path, "a") as f:
                    f.write("\n]")
        except IOError as e:
            logger.error(f"Failed to close JSON file: {e}")

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing escape characters and excess whitespace.

        Args:
            text: Text to clean
        """
        text = re.sub(r"[\n\t\r]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def find_all_links_to_visit(self, soup: bs4.BeautifulSoup) -> None:
        """
        Find all links to visit on the page that match the allowed domain
        and haven't been discovered yet.

        Args:
            soup: BeautifulSoup object of the current page
        """
        # limit to 10 links
        if len(self.links_to_visit) > 10:
            return

        if not soup:
            return

        # Find all links on current page
        for link in soup.find_all("a"):
            href = link.get("href")
            # Only process new links within allowed domain
            if href and self.allowed_domain in href and href not in self.links_to_visit:
                self.links_to_visit.add(href)
                logger.debug(f"Found new link: {href}")

                # Fetch and process the new page
                new_soup = self.get_page_content(href)
                if new_soup:
                    self.find_all_links_to_visit(new_soup)

    def extract_valid_links(self, soup: bs4.BeautifulSoup) -> List[str]:
        """Extract valid links from the page that match the allowed domain.

        Args:
            soup: BeautifulSoup object of the current page

        Returns:
            List of valid links on the page
        """
        links = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and self.allowed_domain in href and href not in self.visited_links:
                links.append(href)
                logger.debug(f"Found valid link: {href}")
        return links

    def process_link(self, link: str) -> None:
        """Process a single link: fetch content, clean it, and save it.

        Args:
            link: URL of the page to
        """
        if link in self.visited_links:
            logger.debug(f"Skipping already visited link: {link}")
            return

        soup = self.get_page_content(link)
        if soup:
            text_content = soup.get_text()
            clean_content = self.clean_text(text_content)
            self.save_content(link, clean_content)
            self.visited_links.add(link)

    def scrape(self) -> None:
        """Main scraping method."""
        logger.info(f"Starting scraping of website: {self.base_url}")

        soup = self.get_page_content(self.base_url)
        if not soup:
            return

        # Find all links recursively
        logger.info("Recrusively finding all links to visit")
        self.find_all_links_to_visit(soup)
        logger.info(
            f"Found {len(self.links_to_visit)} total links to process from {self.base_url}"
        )

        # Process all discovered links with progress bar
        for link in tqdm(self.links_to_visit, desc="Processing links", unit="link"):
            self.process_link(link)

        logger.info(f"Scraping completed successfully for {self.base_url}")
