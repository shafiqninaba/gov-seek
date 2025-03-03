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
import os
from uuid import uuid4
from langchain_text_splitters import RecursiveCharacterTextSplitter


class BaseScraper:
    """Base class for web scraping."""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Initialize WebScraper with base URL and allowed domain."""
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.trusted_url = "https://www.gov.sg/trusted-sites"
        self.logged_limits = False

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
            response = requests.get(
                url, headers=headers, timeout=20
            )  # Added 20 second timeout
            response.raise_for_status()

            return bs4.BeautifulSoup(response.text, "html.parser")

        except requests.Timeout:
            logger.error(f"Request timed out for {url}")
            return None
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
        max_depth: int = 3,
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
        self.max_depth = max_depth
        self.visited_links = set()  # Make sure this is initialized too
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.json_filepath = f"data/scraped_data/{"".join([x if x.isalnum() else "_" for x in self.allowed_domain])}_{self.timestamp}.json"
        logger.info(f"Initialized WebScraper for {self.base_url}")
        logger.info(f"Allowed domain: {self.allowed_domain}")

    def save_content(self, link: str, content: str) -> None:
        """Save scraped content to JSON file.

        Args:
            link: URL of the page
            content: Cleaned text content of the page
        """
        try:
            # Create initial file with empty array if it doesn't exist
            if not os.path.exists(self.json_filepath):
                os.makedirs(os.path.dirname(self.json_filepath), exist_ok=True)
                with open(self.json_filepath, "w") as f:
                    f.write("[\n")

            # Append the new content with proper JSON formatting
            with open(self.json_filepath, "a") as f:
                # Add comma if not first entry
                if os.path.getsize(self.json_filepath) > 2:  # More than just "[\n"
                    f.write(",\n")

                json.dump(
                    {"uuid": str(uuid4()), "link": link, "text": content},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
                logger.debug(f"Saved cleaned content for: {link}")

        except IOError as e:
            logger.error(f"Failed to save data for {link}: {e}")

    def close_json_file(self):
        """Destructor to close the JSON array when scraping is complete."""
        try:
            if os.path.exists(self.json_filepath):
                with open(self.json_filepath, "a") as f:
                    f.write("\n]")
        except Exception as e:
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

    def scrape_recursively(self, url: str, depth: int = 0) -> None:
        """
        Recursively scrape pages while extracting content in the same pass.

        Args:
            url: URL of the page to scrape
            depth: Current depth of recursion
            max_depth: Maximum depth to recurse
        """
        # Check if URL points to a file
        file_extensions = (
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".zip",
            ".rar",
            ".mp3",
            ".mp4",
        )
        if url.lower().endswith(file_extensions):
            logger.debug(f"Skipping file URL: {url}")
            return

        # Check if we've already visited this link or reached max links
        if url in self.visited_links:
            logger.debug(f"Already visited: {url}")
            return
        elif len(self.visited_links) > 10:
            if not self.logged_limits:
                logger.warning("Reached maximum number of links to scrape.")
                self.logged_limits = True
            return
        elif depth > self.max_depth:
            if not self.logged_limits:
                logger.warning("Reached maximum depth.")
                self.logged_limits = True
            return

        # Get and process the page content
        soup = self.get_page_content(url)
        if not soup:
            return

        # Extract and save the content
        text_content = soup.get_text()
        cleaned_content = self.clean_text(text_content)

        chunk_size = 1000
        chunk_overlap = 100
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        splits = text_splitter.split_text(cleaned_content)

        for split_content in splits:
            if split_content:
                self.save_content(url, split_content)
                self.visited_links.add(url)
                logger.debug(f"Processed content for: {url}")

        # Find and process all links on the current page
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and self.allowed_domain in href and href not in self.visited_links:
                logger.debug(f"Found new link: {href}")
                self.scrape_recursively(href, depth + 1)

    def scrape(self) -> None:
        """Main scraping method."""
        logger.info(f"Starting scraping of website: {self.base_url}")

        # Start the recursive scraping from the base URL
        self.scrape_recursively(self.base_url)
        self.close_json_file()
        logger.info(f"Scraping completed. Processed {len(self.visited_links)} pages.")
