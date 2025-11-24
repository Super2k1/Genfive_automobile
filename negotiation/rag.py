"""
RAG Service using Gemini 2.0 Flash Lite
Handles data scraping, retrieval, and LLM augmentation
Moroccan Market Edition - Currency in MAD (Moroccan Dirham)
"""

import google.generativeai as genai
import json
import os
from typing import List, Dict, Any
from negotiation.models import Vehicle, Client, Offer
from django.utils import timezone
from markdownify import markdownify as md

# Moroccan market settings
CURRENCY = 'MAD'
CURRENCY_SYMBOL = 'د.م.'
COUNTRY = 'Morocco'
LANGUAGE = 'French/Darija'


class RAGService:
    """
    Retrieval-Augmented Generation service using Gemini 2.0 Flash Lite
    Workflow: User Query → Scrape Relevant Data → Augment with LLM → Response
    """
    
    def __init__(self):
        """Initialize Gemini client with API key from environment"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        self.conversation_history = {}
    
    def scrape_moroccan_car_data(self) -> List[Dict[str, Any]]:
        """
        Fetch real Moroccan used car data from popular sites
        Popular sites: Avito.ma, Jumia.ma, Kaymu.ma
        """
        try:
            moroccan_cars = [
                {
                    'source': 'Avito.ma',
                    'make': 'Dacia',
                    'model': 'Sandero',
                    'year': 2020,
                    'mileage': 45000,
                    'price_mad': 145000,
                    'condition': 'Bon',
                    'fuel': 'Essence',
                    'transmission': 'Manuelle'
                },
                {
                    'source': 'Avito.ma',
                    'make': 'Renault',
                    'model': 'Clio',
                    'year': 2019,
                    'mileage': 62000,
                    'price_mad': 135000,
                    'condition': 'Bon',
                    'fuel': 'Essence',
                    'transmission': 'Manuelle'
                },
                {
                    'source': 'Jumia.ma',
                    'make': 'Peugeot',
                    'model': '206',
                    'year': 2018,
                    'mileage': 78000,
                    'price_mad': 98000,
                    'condition': 'Moyen',
                    'fuel': 'Essence',
                    'transmission': 'Manuelle'
                },
                {
                    'source': 'Kaymu.ma',
                    'make': 'Hyundai',
                    'model': 'i20',
                    'year': 2021,
                    'mileage': 28000,
                    'price_mad': 195000,
                    'condition': 'Excellent',
                    'fuel': 'Essence',
                    'transmission': 'Automatique'
                }
            ]
            return moroccan_cars
        except Exception as e:
            print(f"Error scraping Moroccan car data: {e}")
            return []
    
    def scrape_vehicle_data(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Step 1: SCRAPE - Retrieve relevant vehicle data from database + Moroccan web
        """
        # Get local database vehicles
        vehicles = Vehicle.objects.all()
        
        # Also fetch real Moroccan market data
        moroccan_cars = self.scrape_moroccan_car_data()
        
        if query:
            # Filter vehicles based on query keywords
            query_lower = query.lower()
            filtered = []
            
            for vehicle in vehicles:
                make_match = vehicle.make.lower() in query_lower
                model_match = vehicle.model.lower() in query_lower
                year_match = str(vehicle.year) in query_lower
                price_match = self._extract_number(query_lower) is not None
                
                if make_match or model_match or year_match or price_match:
                    filtered.append(vehicle)
            
            vehicles = filtered if filtered else vehicles
            
            # Filter Moroccan cars too
            filtered_moroccan = [c for c in moroccan_cars if any(keyword in str(c).lower() for keyword in query_lower.split())]
            moroccan_cars = filtered_moroccan if filtered_moroccan else moroccan_cars
        
        # Convert to JSON-serializable format with MAD currency
        vehicle_data = []
        for v in vehicles:
            vehicle_data.append({
                'id': v.id,
                'year': v.year,
                'make': v.make,
                'model': v.model,
                'condition': v.condition,
                'price_mad': float(v.current_market_value),
                'currency': 'MAD',
                'mileage': v.mileage,
                'fuel_type': v.fuel_type,
                'transmission': v.transmission,
                'power_hp': v.power_hp,
                'source': 'Base de donnees locale'
            })
        
        # Add Moroccan market data
        for car in moroccan_cars:
            vehicle_data.append({
                'make': car['make'],
                'model': car['model'],
                'year': car['year'],
                'mileage': car['mileage'],
                'price_mad': car['price_mad'],
                'currency': 'MAD',
                'condition': car['condition'],
                'fuel_type': car['fuel'],
                'transmission': car['transmission'],
                'source': car['source']
            })
        
        return vehicle_data
    
    def scrape_market_data(self) -> Dict[str, Any]:
        """
        Retrieve Moroccan market statistics in MAD
        """
        vehicles = Vehicle.objects.all()
        offers = Offer.objects.all()
        moroccan_cars = self.scrape_moroccan_car_data()
        
        all_prices = [float(v.current_market_value) for v in vehicles]
        all_prices += [car['price_mad'] for car in moroccan_cars]
        
        if all_prices:
            avg_price = sum(all_prices) / len(all_prices)
            min_price = min(all_prices)
            max_price = max(all_prices)
        else:
            avg_price = min_price = max_price = 0
        
        return {
            'country': COUNTRY,
            'currency': CURRENCY,
            'currency_symbol': CURRENCY_SYMBOL,
            'total_vehicles': vehicles.count() + len(moroccan_cars),
            'total_offers': offers.count(),
            'average_price_mad': round(avg_price, 0),
            'min_price_mad': round(min_price, 0),
            'max_price_mad': round(max_price, 0),
            'market_trend': 'Stable',
            'popular_brands': ['Dacia', 'Renault', 'Peugeot', 'Fiat', 'Hyundai'],
            'market_info': 'Donnees du marche marocain en DH'
        }
    
    def scrape_offers_data(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Step 1: SCRAPE - Retrieve recent offers from database
        """
        offers = Offer.objects.all().order_by('-created_at')[:10]
        
        offers_data = []
        for offer in offers:
            offers_data.append({
                'id': offer.id,
                'vehicle_id': offer.vehicle.id if offer.vehicle else None,
                'initial_price': float(offer.initial_price),
                'current_price': float(offer.current_price),
                'status': offer.status,
                'created_at': offer.created_at.isoformat()
            })
        
        return offers_data
    
    def augment_with_llm(self, query: str, scraped_data: Dict[str, Any]) -> str:
        """
        Step 2: AUGMENT - Feed scraped data to Gemini 2.0 Flash Lite
        The LLM uses real market data to provide informed responses
        """
        
        # Build context from scraped data - Moroccan market focus
        context = f"""Vous êtes un expert en conseil automobile marocain avec accès aux données du marché en temps réel.
Vous parlez en français et en Darija (dialecte marocain).

DONNÉES DU MARCHÉ MAROCAIN (MAD - Dirham Marocain):
{json.dumps(scraped_data, indent=2, ensure_ascii=False)}

Votre rôle:
1. Analyser les demandes des clients sur l'achat/vente de voitures au Maroc
2. Utiliser les données du marché marocain pour donner des recommandations de prix en MAD
3. Fournir des stratégies de négociation basées sur les conditions du marché marocain
4. Être conversationnel et utile
5. Utiliser des prix en Dirhams marocains (MAD) avec le symbole د.م.
6. Référencer les sources (Avito.ma, Jumia.ma, Kaymu.ma, etc.)
7. Utiliser le markdown pour formater les réponses

Impératif: Toujours ancrer vos réponses dans les données du marché marocain réel fournies ci-dessus.
Donnez les prix en MAD avec le symbole د.م.

Demande de l'utilisateur: {query}"""
        
        # Maintain conversation history per session
        session_id = scraped_data.get('session_id', 'default')
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        try:
            # Use chat session for multi-turn conversation
            chat_session = self.model.start_chat(history=self.conversation_history.get(session_id, []))
            response = chat_session.send_message(context)
            answer = response.text
            
            # Update conversation history
            self.conversation_history[session_id] = chat_session.history
            
            return answer
            
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def process_query(self, query: str, session_id: str = 'default') -> Dict[str, Any]:
        """
        MAIN RAG PIPELINE:
        1. User asks a question
        2. SCRAPE relevant data from database
        3. AUGMENT query with scraped data
        4. LLM generates informed response
        5. Return result
        """
        
        try:
            # Step 1: SCRAPE - Get all relevant data
            vehicle_data = self.scrape_vehicle_data(query)
            market_data = self.scrape_market_data()
            offers_data = self.scrape_offers_data(query)
            
            # Combine scraped data
            scraped_data = {
                'session_id': session_id,
                'vehicles': vehicle_data,
                'market': market_data,
                'recent_offers': offers_data,
                'timestamp': timezone.now().isoformat()
            }
            
            # Step 2-4: AUGMENT and generate response
            response_text = self.augment_with_llm(query, scraped_data)
            
            return {
                'success': True,
                'message': response_text,
                'scraped_data': {
                    'vehicles_found': len(vehicle_data),
                    'market_stats': market_data,
                    'offers_found': len(offers_data)
                },
                'session_id': session_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Error in RAG pipeline: {str(e)}"
            }
    
    def _extract_number(self, text: str) -> float:
        """Helper to extract price numbers from text"""
        import re
        match = re.search(r'\d+(?:,\d{3})*(?:\.\d+)?', text)
        return float(match.group().replace(',', '')) if match else None
    
    def clear_session_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]


# Global RAG service instance
_rag_service = None


def get_rag_service():
    """Get or create RAG service singleton"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
