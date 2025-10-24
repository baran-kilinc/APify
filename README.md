# eBay Kleinanzeigen Car Listings Scraper

This Apify Actor scrapes car listings from eBay Kleinanzeigen (German classifieds website). It extracts detailed information about cars including title, price, location, mileage, year, images, and more.

## Features

- **Scrapes car listings** from eBay Kleinanzeigen category or search pages
- **Pagination support** - automatically follows pagination to scrape multiple pages
- **Configurable limit** - set the maximum number of listings to scrape
- **Structured output** - data is stored in a clean, structured format
- **Robust parsing** - handles various HTML structures and missing data gracefully

## Input Parameters

- **startUrl** (required): The URL of the eBay Kleinanzeigen page to scrape
  - Example: `https://www.kleinanzeigen.de/s-autos/c216`
  - Can be a category page or a search results page

- **maxListings** (optional): Maximum number of car listings to scrape
  - Default: 50
  - Set to 0 for unlimited listings
  - Range: 0-1000

## Output

The Actor extracts the following fields for each car listing:

- **title**: Title of the car listing
- **price**: Price of the car
- **location**: Location where the car is located
- **description**: Description of the car
- **imageUrl**: URL of the main image
- **url**: Direct link to the listing page
- **datePosted**: Date when the listing was posted
- **mileage**: Mileage of the car (if available)
- **year**: Year of manufacture (if available)

## Example Input

```json
{
  "startUrl": "https://www.kleinanzeigen.de/s-autos/c216",
  "maxListings": 50
}
```

## Example Output

```json
{
  "title": "VW Golf 7 TDI",
  "price": "12.500 €",
  "location": "Berlin",
  "description": "Gut erhaltener VW Golf 7 TDI, Baujahr 2015",
  "imageUrl": "https://example.com/image.jpg",
  "url": "https://www.kleinanzeigen.de/s-anzeige/vw-golf-tdi-2015/123456789",
  "datePosted": "Heute, 10:30",
  "mileage": "150.000 km",
  "year": "2015"
}
```

## How it works

The Actor uses BeautifulSoup and httpx to scrape the eBay Kleinanzeigen website. It:

1. Fetches the starting URL
2. Parses the HTML to extract car listings
3. Extracts relevant data from each listing
4. Follows pagination links to scrape multiple pages
5. Stops when the maximum number of listings is reached or no more pages are available
6. Stores all data in the Apify dataset

## Local Development

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd APify
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create input file for local testing:
   ```bash
   mkdir -p storage/key_value_stores/default
   ```

4. Create `storage/key_value_stores/default/INPUT.json` with your test input:
   ```json
   {
     "startUrl": "https://www.kleinanzeigen.de/s-autos/c216",
     "maxListings": 5
   }
   ```

5. Run the Actor locally:
   ```bash
   python3 -m src
   ```

### Running Tests

Run the unit tests to verify the parsing logic:

```bash
python3 test_scraper.py
```

### Deployment

To deploy the Actor to Apify platform:

1. Install Apify CLI:
   ```bash
   npm -g install apify-cli
   ```

2. Login to Apify:
   ```bash
   apify login
   ```

3. Deploy the Actor:
   ```bash
   apify push
   ```

## Resources

- [Apify SDK for Python documentation](https://docs.apify.com/sdk/python)
- [Apify Platform documentation](https://docs.apify.com/platform)
- [Python tutorials in Academy](https://docs.apify.com/academy/python)
- [Join our developer community on Discord](https://discord.com/invite/jyEM2PRvMU)
