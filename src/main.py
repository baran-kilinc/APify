"""Module defines the main entry point for the Apify Actor.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from apify import Actor
from bs4 import BeautifulSoup


async def scrape_listing_page(url: str, max_listings: int = 0) -> list[dict[str, Any]]:
    """Scrape car listings from eBay Kleinanzeigen page.
    
    Args:
        url: The URL to scrape
        max_listings: Maximum number of listings to scrape (0 = unlimited)
        
    Returns:
        List of dictionaries containing car listing data
    """
    listings = []
    page_num = 1
    base_url = url
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        while True:
            # Construct page URL
            if page_num > 1:
                # Add page parameter to URL
                if '?' in base_url:
                    current_url = f"{base_url}&page={page_num}"
                else:
                    current_url = f"{base_url}?page={page_num}"
            else:
                current_url = base_url
                
            Actor.log.info(f"Scraping page {page_num}: {current_url}")
            
            try:
                response = await client.get(current_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                response.raise_for_status()
            except Exception as e:
                Actor.log.error(f"Failed to fetch page {page_num}: {e}")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all listing articles - eBay Kleinanzeigen uses article tags with specific classes
            # The structure may vary, so we'll look for common patterns
            article_list = soup.find_all('article', class_=re.compile(r'aditem'))
            
            if not article_list:
                # Try alternative selectors
                article_list = soup.find_all('li', class_=re.compile(r'ad-listitem'))
            
            if not article_list:
                Actor.log.info(f"No more listings found on page {page_num}")
                break
                
            Actor.log.info(f"Found {len(article_list)} listings on page {page_num}")
            
            for article in article_list:
                try:
                    listing = extract_listing_data(article, base_url)
                    if listing:
                        listings.append(listing)
                        
                        # Check if we've reached the limit
                        if max_listings > 0 and len(listings) >= max_listings:
                            Actor.log.info(f"Reached maximum listings limit: {max_listings}")
                            return listings
                            
                except Exception as e:
                    Actor.log.warning(f"Failed to extract listing data: {e}")
                    continue
            
            # Check if there's a next page
            next_page = soup.find('a', class_=re.compile(r'pagination-next'))
            if not next_page or not next_page.get('href'):
                Actor.log.info("No more pages to scrape")
                break
                
            page_num += 1
            
    return listings


def extract_listing_data(article: Any, base_url: str) -> dict[str, Any] | None:
    """Extract data from a single listing article.
    
    Args:
        article: BeautifulSoup element containing the listing
        base_url: Base URL for resolving relative links
        
    Returns:
        Dictionary with listing data or None if extraction fails
    """
    try:
        listing = {}
        
        # Extract title and URL - try multiple selectors
        title_elem = article.find('a', class_=re.compile(r'ellipsis'))
        if not title_elem:
            # Try finding any link in h2 tag
            h2_tag = article.find('h2')
            if h2_tag:
                title_elem = h2_tag.find('a')
        if not title_elem:
            # Try any link in the article
            title_elem = article.find('a')
            
        if title_elem:
            listing['title'] = title_elem.get_text(strip=True)
            
            # Extract URL from title link
            if title_elem.get('href'):
                listing['url'] = urljoin(base_url, title_elem['href'])
            else:
                listing['url'] = ''
        else:
            listing['url'] = ''
        
        # Extract price
        price_elem = article.find('p', class_=re.compile(r'aditem-main--middle--price'))
        if not price_elem:
            price_elem = article.find('span', class_=re.compile(r'price'))
        if price_elem:
            listing['price'] = price_elem.get_text(strip=True)
        else:
            listing['price'] = 'N/A'
        
        # Extract location
        location_elem = article.find('div', class_=re.compile(r'aditem-main--top--left'))
        if location_elem:
            location_text = location_elem.get_text(strip=True)
            listing['location'] = location_text
        else:
            listing['location'] = 'N/A'
        
        # Extract description
        desc_elem = article.find('p', class_=re.compile(r'aditem-main--middle--description'))
        if desc_elem:
            listing['description'] = desc_elem.get_text(strip=True)
        else:
            listing['description'] = ''
        
        # Extract image URL
        img_elem = article.find('img')
        if img_elem and img_elem.get('src'):
            listing['imageUrl'] = img_elem['src']
        else:
            listing['imageUrl'] = ''
        
        # Extract additional details if available
        details_elem = article.find('div', class_=re.compile(r'aditem-main--middle'))
        if details_elem:
            details_text = details_elem.get_text()
            
            # Try to extract year
            year_match = re.search(r'\b(19|20)\d{2}\b', details_text)
            if year_match:
                listing['year'] = year_match.group(0)
            else:
                listing['year'] = ''
            
            # Try to extract mileage
            mileage_match = re.search(r'([\d.]+)\s*km', details_text, re.IGNORECASE)
            if mileage_match:
                listing['mileage'] = mileage_match.group(0)
            else:
                listing['mileage'] = ''
        else:
            listing['year'] = ''
            listing['mileage'] = ''
        
        # Extract date posted
        date_elem = article.find('div', class_=re.compile(r'aditem-main--top--right'))
        if date_elem:
            listing['datePosted'] = date_elem.get_text(strip=True)
        else:
            listing['datePosted'] = ''
        
        # Only return if we have at least a title
        if listing.get('title'):
            return listing
            
    except Exception as e:
        Actor.log.warning(f"Error extracting listing data: {e}")
        
    return None


async def main() -> None:
    """Define a main entry point for the Apify Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Apify platform, and it also enhances performance in
    the field of web scraping significantly.
    """
    async with Actor:
        Actor.log.info('eBay Kleinanzeigen Car Scraper started')
        
        # Get input from Actor
        actor_input = await Actor.get_input() or {}
        start_url = actor_input.get('startUrl')
        max_listings = actor_input.get('maxListings', 50)
        
        # Validate input
        if not start_url:
            Actor.log.error('Missing required input: startUrl')
            return
        
        Actor.log.info(f"Starting scrape of {start_url} with max listings: {max_listings}")
        
        # Scrape listings
        try:
            listings = await scrape_listing_page(start_url, max_listings)
            
            Actor.log.info(f"Successfully scraped {len(listings)} listings")
            
            # Push data to dataset
            if listings:
                await Actor.push_data(listings)
                Actor.log.info(f"Pushed {len(listings)} listings to dataset")
            else:
                Actor.log.warning("No listings were scraped")
                
        except Exception as e:
            Actor.log.error(f"Scraping failed: {e}")
            raise
