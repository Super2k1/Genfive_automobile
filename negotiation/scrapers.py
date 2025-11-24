"""
Scraping utilities for market data collection
"""
import requests
from bs4 import BeautifulSoup
import logging
from decimal import Decimal
from typing import List, Dict, Any
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class MarketDataScraper:
    """
    Scrapes market data from various sources to collect price information
    for used vehicles
    """
    
    def __init__(self):
        self.session = self._create_session()
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def scrape_leboncoin(self, make: str, model: str, year: int, fuel: str) -> Dict[str, Any]:
        """
        Scrape price data from LeBonCoin
        (Implementation would require proper parsing of LeBonCoin listings)
        """
        try:
            # This is a mock implementation for demonstration
            # In production, implement proper scraping with selenium for dynamic content
            url = f"https://www.leboncoin.fr/search"
            params = {
                'text': f'{year} {make} {model}',
                'category': 2,
                'fuel': self._get_fuel_code(fuel),
            }
            
            headers = {'User-Agent': self.user_agent}
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse and extract data
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('a', class_='_2tria')
            
            prices = []
            for listing in listings[:10]:  # Get first 10 listings
                try:
                    price_elem = listing.find('h3')
                    if price_elem:
                        price_text = price_elem.text.strip()
                        price = Decimal(price_text.replace('€', '').replace(' ', '').split(',')[0])
                        prices.append(price)
                except (ValueError, AttributeError):
                    continue
            
            if prices:
                return {
                    'source': 'leboncoin',
                    'average_price': sum(prices) / len(prices),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'listings_count': len(prices),
                }
            
        except Exception as e:
            logger.error(f"Error scraping LeBonCoin: {str(e)}")
        
        return None
    
    def scrape_argus(self, make: str, model: str, year: int) -> Dict[str, Any]:
        """
        Scrape price data from Argus (used car valuation)
        """
        try:
            # This is a mock implementation
            # Argus requires specific API access or specialized scraping
            url = "https://api.argusinternetp.com/search"
            
            params = {
                'make': make,
                'model': model,
                'year': year,
            }
            
            headers = {'User-Agent': self.user_agent}
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'source': 'argus',
                'average_price': Decimal(str(data.get('price', 0))),
                'confidence': data.get('confidence', 0.8),
            }
            
        except Exception as e:
            logger.error(f"Error scraping Argus: {str(e)}")
        
        return None
    
    def scrape_webmoteurs(self, make: str, model: str, year: int) -> Dict[str, Any]:
        """
        Scrape price data from Webmoteurs
        """
        try:
            url = f"https://www.webmoteurs.com"
            
            params = {
                'marque': make,
                'modele': model,
                'annee': year,
            }
            
            headers = {'User-Agent': self.user_agent}
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('div', class_='annonce')
            
            prices = []
            mileages = []
            
            for listing in listings[:15]:
                try:
                    price_elem = listing.find('span', class_='prix')
                    if price_elem:
                        price = Decimal(price_elem.text.strip().replace('€', '').replace(' ', ''))
                        prices.append(price)
                    
                    km_elem = listing.find('span', class_='km')
                    if km_elem:
                        km = int(km_elem.text.strip().replace('km', '').replace(' ', ''))
                        mileages.append(km)
                
                except (ValueError, AttributeError):
                    continue
            
            if prices:
                return {
                    'source': 'webmoteurs',
                    'average_price': sum(prices) / len(prices),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'listings_count': len(prices),
                    'average_mileage': sum(mileages) / len(mileages) if mileages else None,
                }
        
        except Exception as e:
            logger.error(f"Error scraping Webmoteurs: {str(e)}")
        
        return None
    
    def scrape_caradisiac(self, make: str, model: str, year: int) -> Dict[str, Any]:
        """
        Scrape price data from Caradisiac
        """
        try:
            url = "https://www.caradisiac.com/annonces"
            
            params = {
                'make': make,
                'model': model,
                'year': year,
            }
            
            headers = {'User-Agent': self.user_agent}
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            prices = []
            
            for item in soup.find_all('div', class_='c-card-listing-item')[:20]:
                try:
                    price_elem = item.find('p', class_='price')
                    if price_elem:
                        price_text = price_elem.text.strip().replace('€', '').replace(' ', '')
                        price = Decimal(price_text)
                        prices.append(price)
                except (ValueError, AttributeError):
                    continue
            
            if prices:
                return {
                    'source': 'caradisiac',
                    'average_price': sum(prices) / len(prices),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'listings_count': len(prices),
                }
        
        except Exception as e:
            logger.error(f"Error scraping Caradisiac: {str(e)}")
        
        return None
    
    def aggregate_market_data(self, make: str, model: str, year: int, fuel: str) -> Dict[str, Any]:
        """
        Aggregate market data from multiple sources
        """
        results = {
            'make': make,
            'model': model,
            'year': year,
            'fuel_type': fuel,
            'sources': {}
        }
        
        # Scrape from multiple sources
        sources = [
            ('leboncoin', self.scrape_leboncoin(make, model, year, fuel)),
            ('webmoteurs', self.scrape_webmoteurs(make, model, year)),
            ('caradisiac', self.scrape_caradisiac(make, model, year)),
            ('argus', self.scrape_argus(make, model, year)),
        ]
        
        valid_sources = []
        for source_name, data in sources:
            if data:
                results['sources'][source_name] = data
                valid_sources.append(data)
        
        # Calculate aggregate statistics
        if valid_sources:
            prices = []
            for source in valid_sources:
                if 'average_price' in source:
                    prices.append(source['average_price'])
            
            if prices:
                results['aggregate'] = {
                    'average_price': sum(prices) / len(prices),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'sources_count': len(valid_sources),
                }
        
        return results
    
    def _get_fuel_code(self, fuel: str) -> str:
        """Convert fuel type to code for API"""
        fuel_map = {
            'essence': '1',
            'diesel': '2',
            'hybride': '3',
            'electrique': '4',
        }
        return fuel_map.get(fuel, '0')
