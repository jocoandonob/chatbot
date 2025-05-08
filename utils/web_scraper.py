import logging
import trafilatura
from typing import Optional

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> Optional[str]:
    """
    Extract the main text content from a website URL.
    
    Args:
        url: The URL of the website to scrape.
        
    Returns:
        The extracted text content or None if the extraction failed.
    """
    try:
        logger.info(f"Fetching content from URL: {url}")
        # Download the web page
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded is None:
            logger.error(f"Failed to download content from URL: {url}")
            return None
        
        # Extract the main content
        text = trafilatura.extract(downloaded)
        
        if text is None or text.strip() == "":
            logger.error(f"No content extracted from URL: {url}")
            return None
            
        logger.info(f"Successfully extracted {len(text)} characters from URL: {url}")
        return text
        
    except Exception as e:
        logger.error(f"Error extracting content from URL: {str(e)}")
        return None