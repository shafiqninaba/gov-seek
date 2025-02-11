import bs4
import requests
import json
from loguru import logger
import re
# TODO: add a list of visited links to avoid revisiting the same link
# TODO: implement recursive scraping to follow links on the page

# Configure logger
logger.add("logs/info.log", rotation="10 MB", format="{time} {level} {message}", level="INFO")
logger.add("logs/error.log", rotation="10 MB", format="{time} {level} {message}", level="ERROR")
logger.add("logs/debug.log", rotation="10 MB", format="{time} {level} {message}", level="DEBUG")

my_website = "https://www.activesgcircle.gov.sg/activehealth"
allowed_domain = "activesgcircle.gov.sg"

def clean_text(text):
    """Clean text by removing escape characters and excess whitespace."""
    # Replace escape characters with space
    text = re.sub(r'[\n\t\r]', ' ', text)
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    logger.info(f"Starting scraping of website: {my_website}")
    
    try:
        response = requests.get(my_website)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch main website: {e}")
        return

    logger.debug("Extracting all links from the page")
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            logger.debug(f"Skipping empty href")
            continue
        if allowed_domain in href:
            links.append(href)
            logger.debug(f"Found valid link: {href}")

    logger.info(f"Found {len(links)} valid links to process")

    for link in links:
        try:
            logger.info(f"Processing link: {link}")
            response = requests.get(link)
            response.raise_for_status()
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text()
            clean_content = clean_text(text_content)
            
            with open("data/data.json", "a") as f:
                json.dump({"link": link, "text": clean_content}, f)
                f.write("\n")
                logger.debug(f"Saved cleaned content for: {link}")
                
        except requests.RequestException as e:
            logger.error(f"Failed to process link {link}: {e}")
        except IOError as e:
            logger.error(f"Failed to save data for {link}: {e}")

    logger.info("Scraping completed successfully")

if __name__ == "__main__":
    main()