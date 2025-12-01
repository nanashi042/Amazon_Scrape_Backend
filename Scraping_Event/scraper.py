import re
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from urllib.parse import urlparse, parse_qs
import random
import time


# List of realistic user agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
]


def get_headers(url=''):
    """Return headers with random user agent"""
    # Determine domain for referer
    if 'amazon.in' in url:
        referer = 'https://www.amazon.in/'
    elif 'amazon.co.uk' in url:
        referer = 'https://www.amazon.co.uk/'
    elif 'amazon.de' in url:
        referer = 'https://www.amazon.de/'
    else:
        referer = 'https://www.amazon.com/'
    
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'max-age=0',
        'Pragma': 'no-cache',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': referer,
        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="120", "Chromium";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }


def extract_asin_from_url(url):
    """Extract ASIN from Amazon URL"""
    # ASIN format: /dp/B0XXXXXXXX or /gp/product/B0XXXXXXXX
    match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    return None


def scrape_amazon_product(url):
    """
    Scrape Amazon product details from URL
    Works with amazon.com, amazon.in, amazon.co.uk, etc.
    Returns dict with product information
    Note: Amazon heavily uses JavaScript rendering, so extraction may be limited.
    """
    try:
        # Get ASIN from URL
        asin = extract_asin_from_url(url)
        if not asin:
            return {'error': 'Invalid Amazon product URL. Could not extract ASIN.'}

        # Get headers with random user agent, passing URL for better referer
        headers = get_headers(url)
        
        # Make request with retry logic and session for persistence
        response = None
        session = requests.Session()
        
        for attempt in range(3):
            try:
                response = session.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    break
                # Add delay before retry
                time.sleep(1)
            except:
                if attempt == 2:
                    raise
                time.sleep(1)
                continue

        if not response or response.status_code != 200:
            return {'error': f'Failed to fetch URL. Status code: {response.status_code if response else "Unknown"}'}

        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = response.text

        # Extract product title - comprehensive approach with multiple fallbacks
        title = None
        
        # Try method 1: ID-based selectors
        title_element = soup.find('span', {'id': 'productTitle'})
        if title_element:
            title = title_element.get_text(strip=True)
        
        # Try method 2: Look for h1
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
        
        # Try method 3: Find span with specific classes
        if not title:
            title_spans = soup.find_all('span', {'class': re.compile(r'a-size-large|product-title')}, limit=5)
            for span in title_spans:
                text = span.get_text(strip=True)
                if text and len(text) > 10:
                    title = text
                    break
        
        # Try method 4: Regex search in page text (look for title pattern)
        if not title:
            # Look for common title patterns in HTML
            title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', page_text, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
        
        # Try method 5: Look for og:title meta tag
        if not title:
            og_title = soup.find('meta', {'property': 'og:title'})
            if og_title and og_title.get('content'):
                title = og_title['content'].strip()
        
        # Fallback to Unknown if nothing found
        if not title:
            title = 'Unknown'

        # Extract price - comprehensive approach
        current_price = Decimal('0.00')
        original_price = None
        currency = 'USD'  # Default currency
        
        # Determine currency based on domain
        if 'amazon.in' in url:
            currency = 'INR'
        elif 'amazon.co.uk' in url or 'amazon.uk' in url:
            currency = 'GBP'
        elif 'amazon.de' in url or 'amazon.fr' in url or 'amazon.es' in url:
            currency = 'EUR'
        elif 'amazon.ca' in url:
            currency = 'CAD'
        elif 'amazon.au' in url:
            currency = 'AUD'
        
        page_text = response.text
        
        # Try multiple price selector patterns
        price_selectors = [
            {'class': re.compile(r'a-price-whole')},
            {'class': re.compile(r'a-price-fraction')},
            {'data-a-color': 'price'},
            {'class': re.compile(r'a-price-symbol')},
            {'id': re.compile(r'priceblock|offer-price')},
        ]
        
        for selector in price_selectors:
            price_elements = soup.find_all('span', selector, limit=10)
            for price_element in price_elements:
                price_text = price_element.get_text(strip=True)
                
                # Try to extract price value
                price_match = re.search(
                    r'(?:₹|£|€|\$|C\$|A\$)?\s*([0-9,]+(?:\.[0-9]{0,2})?)',
                    price_text
                )
                
                if price_match:
                    price_str = price_match.group(1).replace(',', '').strip()
                    try:
                        temp_price = Decimal(price_str)
                        if temp_price > 0:
                            current_price = temp_price
                            break
                    except:
                        continue
            
            if current_price > 0:
                break

        # If no price found in HTML, search in page text with regex by currency
        if current_price <= 0:
            # Indian Rupee
            rupee_match = re.search(
                r'₹[\s]*([0-9,]+(?:\.[0-9]{0,2})?)',
                page_text
            )
            if rupee_match:
                price_str = rupee_match.group(1).replace(',', '')
                try:
                    current_price = Decimal(price_str)
                    currency = 'INR'
                except:
                    pass
            
            # US Dollar
            if current_price <= 0:
                dollar_match = re.search(
                    r'\$\s*([0-9,]+(?:\.[0-9]{0,2})?)',
                    page_text
                )
                if dollar_match:
                    price_str = dollar_match.group(1).replace(',', '')
                    try:
                        current_price = Decimal(price_str)
                        currency = 'USD'
                    except:
                        pass
            
            # British Pound
            if current_price <= 0:
                pound_match = re.search(
                    r'£\s*([0-9,]+(?:\.[0-9]{0,2})?)',
                    page_text
                )
                if pound_match:
                    price_str = pound_match.group(1).replace(',', '')
                    try:
                        current_price = Decimal(price_str)
                        currency = 'GBP'
                    except:
                        pass
            
            # Euro
            if current_price <= 0:
                euro_match = re.search(
                    r'€\s*([0-9,]+(?:\.[0-9]{0,2})?)',
                    page_text
                )
                if euro_match:
                    price_str = euro_match.group(1).replace(',', '')
                    try:
                        current_price = Decimal(price_str)
                        currency = 'EUR'
                    except:
                        pass
            
            # Canadian Dollar
            if current_price <= 0:
                cad_match = re.search(
                    r'C\$\s*([0-9,]+(?:\.[0-9]{0,2})?)',
                    page_text
                )
                if cad_match:
                    price_str = cad_match.group(1).replace(',', '')
                    try:
                        current_price = Decimal(price_str)
                        currency = 'CAD'
                    except:
                        pass

        # Extract original/list price with better selectors
        original_selectors = [
            {'class': re.compile(r'a-price-alternate|strikethrough')},
            {'class': re.compile(r'basisPrice')},
            {'id': re.compile(r'priceblock_dealprice')},
        ]
        
        for selector in original_selectors:
            original_element = soup.find('span', selector)
            if original_element:
                price_text = original_element.get_text(strip=True)
                price_match = re.search(
                    r'(?:₹|£|€|\$)?\s*([0-9,]+(?:\.[0-9]{0,2})?)',
                    price_text
                )
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    try:
                        original_price = Decimal(price_str)
                        break
                    except:
                        continue

        # Extract rating - improved selectors
        rating = None
        rating_selectors = [
            {'class': re.compile(r'a-icon-star-small|a-star-small')},
            {'class': re.compile(r'a-icon-star|a-star')},
            {'id': re.compile(r'acrPopover')},
        ]
        
        for selector in rating_selectors:
            rating_element = soup.find('span', selector)
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    try:
                        rating = float(rating_match.group(1))
                        if 0 <= rating <= 5:
                            break
                        rating = None
                    except:
                        rating = None

        # Extract number of reviews - improved selectors
        number_of_reviews = 0
        review_selectors = [
            {'id': re.compile(r'acrCustomerReviewText')},
            {'class': re.compile(r'a-count')},
            {'id': re.compile(r'reviews-count')},
        ]
        
        for selector in review_selectors:
            reviews_element = soup.find('span', selector)
            if reviews_element:
                reviews_text = reviews_element.get_text(strip=True)
                reviews_match = re.search(r'([0-9,]+)', reviews_text)
                if reviews_match:
                    try:
                        number_of_reviews = int(
                            reviews_match.group(1).replace(',', '')
                        )
                        if number_of_reviews > 0:
                            break
                    except:
                        continue

        # Extract image URL - multiple approaches
        image_url = None
        image_selectors = [
            {'id': 'landingImage'},
            {'id': 'imageBlock'},
            {'class': re.compile(r'a-dynamic-image|product-image')},
        ]
        
        for selector in image_selectors:
            image_element = soup.find('img', selector)
            if image_element:
                if image_element.get('src'):
                    image_url = image_element['src']
                    break
                elif image_element.get('data-old-src'):
                    image_url = image_element.get('data-old-src')
                    break

        # If still no image, search in all imgs
        if not image_url:
            img_tags = soup.find_all('img', limit=100)
            for img in img_tags:
                src = img.get('src', '')
                # Look for product images
                if any(pattern in src for pattern in [
                    '/images/I/',
                    'm.media-amazon.com',
                    'product',
                    'item'
                ]):
                    if not any(pattern in src for pattern in [
                        'nav',
                        'logo',
                        'sprite',
                        'icon'
                    ]):
                        image_url = src
                        break

        # Determine availability with better detection
        availability = 'In Stock'
        if re.search(r'out of stock|unavailable|not available', page_text, re.IGNORECASE):
            availability = 'Out of Stock'
        elif re.search(r'only \d+ (left|remaining)', page_text, re.IGNORECASE):
            availability = 'Limited Stock'

        return {
            'asin': asin,
            'title': title,
            'current_price': float(current_price),
            'original_price': float(original_price) if original_price else None,
            'currency': currency,
            'rating': rating,
            'number_of_reviews': number_of_reviews,
            'image_url': image_url,
            'availability': availability,
        }

    except requests.exceptions.Timeout:
        return {'error': 'Request timed out. Amazon took too long to respond.'}
    except requests.RequestException as e:
        return {'error': f'Failed to fetch URL: {str(e)}'}
    except Exception as e:
        return {'error': f'Failed to scrape product: {str(e)}'}
