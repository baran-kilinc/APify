"""Test the scraper parsing logic with mock HTML."""

from bs4 import BeautifulSoup
from src.main import extract_listing_data


def test_extract_listing_data():
    """Test extraction of listing data from mock HTML."""
    
    # Mock HTML similar to eBay Kleinanzeigen structure
    mock_html = """
    <article class="aditem">
        <div class="aditem-main">
            <div class="aditem-main--top">
                <div class="aditem-main--top--left">Berlin</div>
                <div class="aditem-main--top--right">Heute, 10:30</div>
            </div>
            <div class="aditem-main--middle">
                <a href="/s-anzeige/vw-golf-tdi-2015/123456789" class="ellipsis">
                    VW Golf 7 TDI 2015
                </a>
                <p class="aditem-main--middle--description">
                    Gut erhaltener VW Golf 7 TDI, Baujahr 2015, 150.000 km
                </p>
                <p class="aditem-main--middle--price">12.500 €</p>
            </div>
        </div>
        <div class="aditem-image">
            <img src="https://example.com/image.jpg" alt="VW Golf">
        </div>
    </article>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    article = soup.find('article')
    
    listing = extract_listing_data(article, 'https://www.kleinanzeigen.de')
    
    print("Extracted listing data:")
    for key, value in listing.items():
        print(f"  {key}: {value}")
    
    # Verify key fields are extracted
    assert listing is not None, "Listing should not be None"
    assert listing.get('title') == 'VW Golf 7 TDI 2015', f"Title mismatch: {listing.get('title')}"
    assert listing.get('price') == '12.500 €', f"Price mismatch: {listing.get('price')}"
    assert listing.get('location') == 'Berlin', f"Location mismatch: {listing.get('location')}"
    assert listing.get('url') == 'https://www.kleinanzeigen.de/s-anzeige/vw-golf-tdi-2015/123456789', f"URL mismatch: {listing.get('url')}"
    assert listing.get('imageUrl') == 'https://example.com/image.jpg', f"Image URL mismatch: {listing.get('imageUrl')}"
    assert listing.get('description'), "Description should not be empty"
    assert listing.get('datePosted') == 'Heute, 10:30', f"Date posted mismatch: {listing.get('datePosted')}"
    assert listing.get('mileage') == '150.000 km', f"Mileage mismatch: {listing.get('mileage')}"
    assert listing.get('year') == '2015', f"Year mismatch: {listing.get('year')}"
    
    print("\n✓ All assertions passed!")
    print("\nTest completed successfully!")


def test_extract_listing_data_alternative_structure():
    """Test extraction with alternative HTML structure (li element with ad-listitem class)."""
    
    mock_html = """
    <li class="ad-listitem">
        <h2>
            <a href="/s-anzeige/mercedes-c-klasse-2018/987654321">
                Mercedes C-Klasse 2018
            </a>
        </h2>
        <span class="price">VB 25.000 €</span>
        <div class="aditem-main--top--left">München</div>
        <img src="https://example.com/mercedes.jpg" alt="Mercedes">
    </li>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    article = soup.find('li')
    
    listing = extract_listing_data(article, 'https://www.kleinanzeigen.de')
    
    print("\nExtracted listing data (alternative structure):")
    for key, value in listing.items():
        print(f"  {key}: {value}")
    
    assert listing is not None, "Listing should not be None"
    assert listing.get('title') == 'Mercedes C-Klasse 2018', f"Title mismatch: {listing.get('title')}"
    assert listing.get('price') == 'VB 25.000 €', f"Price mismatch: {listing.get('price')}"
    assert listing.get('url') == 'https://www.kleinanzeigen.de/s-anzeige/mercedes-c-klasse-2018/987654321', f"URL mismatch: {listing.get('url')}"
    
    print("\n✓ All assertions passed for alternative structure!")


def test_extract_listing_missing_fields():
    """Test extraction when some fields are missing."""
    
    mock_html = """
    <article class="aditem">
        <a href="/s-anzeige/bmw-3er/111222333" class="ellipsis">
            BMW 3er
        </a>
    </article>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    article = soup.find('article')
    
    listing = extract_listing_data(article, 'https://www.kleinanzeigen.de')
    
    print("\nExtracted listing data (minimal fields):")
    for key, value in listing.items():
        print(f"  {key}: {value}")
    
    assert listing is not None, "Listing should not be None even with missing fields"
    assert listing.get('title') == 'BMW 3er', f"Title mismatch: {listing.get('title')}"
    assert listing.get('price') == 'N/A', f"Price should be N/A when missing: {listing.get('price')}"
    assert listing.get('location') == 'N/A', f"Location should be N/A when missing: {listing.get('location')}"
    
    print("\n✓ All assertions passed for missing fields!")


if __name__ == '__main__':
    test_extract_listing_data()
    test_extract_listing_data_alternative_structure()
    test_extract_listing_missing_fields()
    print("\n" + "="*50)
    print("All tests passed successfully! ✓")
    print("="*50)
