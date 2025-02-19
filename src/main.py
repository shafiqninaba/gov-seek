"""Main module for the data pipeline."""

from loguru import logger
from data_pipeline.crawler import WebScraper, BaseScraper
import re


def configure_logger() -> None:
    """Configure logging settings."""
    logger.add(
        "logs/info.log",
        rotation="10 MB",
        format="{time} {level} {message}",
        level="INFO",
    )
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        format="{time} {level} {message}",
        level="ERROR",
    )
    logger.add(
        "logs/debug.log",
        rotation="10 MB",
        format="{time} {level} {message}",
        level="DEBUG",
    )


def main():
    """Main function for the data pipeline. This function scrapes the data from the source website and saves it to the database."""
    configure_logger()
    source_scraper = BaseScraper()
    links = source_scraper.extract_tbody_links()
    for link in links:
        logger.info(f"Scraping link: {link}")
        scraper = WebScraper(
            base_url=link,
            allowed_domain=re.search(r"https?://(.[^/]*)/*", link).group(1),
            min_delay=0.0,
            max_delay=0.0,
        )
        scraper.scrape()


if __name__ == "__main__":
    main()
