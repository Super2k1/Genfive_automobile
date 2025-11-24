"""
Negotiation orchestration and business logic
"""
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from negotiation.models import (
    Negotiation, Vehicle, Client, Offer, NegotiationRound, MarketData
)
from negotiation.agents import (
    MarketAnalysisAgent, TradeInEvaluationAgent, 
    OfferStructuringAgent, NegotiationAgent
)
from negotiation.scrapers import MarketDataScraper

logger = logging.getLogger(__name__)


class NegotiationOrchestrator:
    """
    Orchestrates the entire negotiation process
    """
    
    def __init__(self):
        self.market_analyzer = MarketAnalysisAgent()
        self.trade_in_evaluator = TradeInEvaluationAgent()
        self.offer_structurer = OfferStructuringAgent()
        self.negotiator = NegotiationAgent()
        self.scraper = MarketDataScraper()
    
    def initiate_negotiation(self, 
                            client_id: int,
                            trade_in_vehicle_id: Optional[int] = None,
                            target_vehicle_id: Optional[int] = None,
                            business_margin_target: float = 0.15) -> Negotiation:
        """
        Initiate a complete negotiation process
        """
        
        try:
            client = Client.objects.get(id=client_id)
            
            # Get or create negotiation
            negotiation = Negotiation.objects.create(
                client=client,
                trade_in_vehicle_id=trade_in_vehicle_id,
                target_vehicle_id=target_vehicle_id,
                status='initiated'
            )
            
            # If no target vehicle specified, use client's preferred vehicle
            if not target_vehicle_id:
                target_vehicle = self._find_suitable_vehicle(client)
                if target_vehicle:
                    negotiation.target_vehicle = target_vehicle
                    negotiation.save()
            
            # Get market data
            if negotiation.trade_in_vehicle:
                market_data = self._get_or_scrape_market_data(
                    negotiation.trade_in_vehicle
                )
                
                # Store market analysis
                market_analyzer = MarketAnalysisAgent()
                market_analysis = market_analyzer.analyze_market(
                    self._vehicle_to_dict(negotiation.trade_in_vehicle),
                    market_data
                )
                negotiation.market_analysis = market_analysis
            
            # Initiate negotiation strategy
            business_objectives = {
                'target_margin': business_margin_target,
                'volume_target': 1,
                'satisfaction_priority': 0.7,
            }
            
            strategy = self.negotiator.initiate_negotiation(
                self._client_to_dict(client),
                self._vehicle_to_dict(negotiation.trade_in_vehicle) if negotiation.trade_in_vehicle else {},
                negotiation.market_analysis,
                business_objectives
            )
            
            negotiation.agent_reasoning = strategy
            negotiation.status = 'in_progress'
            negotiation.save()
            
            logger.info(f"Negotiation {negotiation.id} initiated")
            
            return negotiation
        
        except Client.DoesNotExist:
            logger.error(f"Client {client_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error initiating negotiation: {str(e)}")
            raise
    
    def execute_negotiation_round(self, negotiation_id: int, 
                                  client_feedback: str = "") -> Dict[str, Any]:
        """
        Execute a negotiation round
        """
        
        try:
            negotiation = Negotiation.objects.get(id=negotiation_id)
            
            # Check if max rounds reached
            if negotiation.negotiation_rounds >= negotiation.max_rounds:
                logger.warning(f"Negotiation {negotiation_id} reached max rounds")
                return {"status": "max_rounds_reached"}
            
            negotiation.negotiation_rounds += 1
            
            # Get current best offer
            current_offer = negotiation.offers.order_by('-created_at').first()
            if not current_offer:
                current_offer = self._create_initial_offer(negotiation)
            
            # Process negotiation round
            round_result = self.negotiator.process_round(
                self._offer_to_dict(current_offer),
                client_feedback,
                negotiation.negotiation_rounds,
                negotiation.max_rounds
            )
            
            # Create negotiation round record
            round_record = NegotiationRound.objects.create(
                negotiation=negotiation,
                round_number=negotiation.negotiation_rounds,
                agent_proposal=round_result.get('proposed_offer', {}),
                agent_reasoning=round_result.get('reasoning', ''),
                client_feedback=client_feedback,
                round_status='ongoing'
            )
            
            # Check if deal is concluded
            if round_result.get('should_conclude', False):
                negotiation.status = 'concluded'
                negotiation.final_price = Decimal(str(round_result.get('final_price', 0)))
                negotiation.margin_achieved = Decimal(str(round_result.get('margin', 0)))
                negotiation.ended_at = datetime.now()
            
            negotiation.save()
            
            return {
                'round_number': negotiation.negotiation_rounds,
                'proposed_offer': round_result.get('proposed_offer', {}),
                'status': negotiation.status,
                'should_continue': not round_result.get('should_conclude', False),
                'confidence': round_result.get('confidence_score', 0),
            }
        
        except Negotiation.DoesNotExist:
            logger.error(f"Negotiation {negotiation_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error executing negotiation round: {str(e)}")
            raise
    
    def _create_initial_offer(self, negotiation: Negotiation) -> Offer:
        """
        Create initial offer using AI agent
        """
        
        if not negotiation.target_vehicle:
            raise ValueError("Target vehicle not set for negotiation")
        
        # Get market data if available
        market_data = self._get_or_scrape_market_data(negotiation.target_vehicle)
        
        # Structure offers
        offer_types = [negotiation.client.subscription_preference] if negotiation.client.subscription_preference != 'flexible' else ['achat', 'lld', 'abonnement']
        
        business_objectives = {
            'target_margin': 0.15,
            'satisfaction_priority': 0.7,
        }
        
        client_budget = (
            negotiation.client.budget_min or Decimal('10000'),
            negotiation.client.budget_max or Decimal('50000')
        )
        
        offer_data = self.offer_structurer.structure_offer(
            self._vehicle_to_dict(negotiation.target_vehicle),
            float(negotiation.trade_in_offered_value or 0),
            offer_types,
            (float(client_budget[0]), float(client_budget[1])),
            business_objectives
        )
        
        # Create Offer object
        offers = offer_data.get('offers', [])
        if offers:
            best_offer = offers[0]  # Take first/best offer
            
            offer = Offer.objects.create(
                negotiation=negotiation,
                offer_type=best_offer.get('offer_type', 'achat'),
                vehicle=negotiation.target_vehicle,
                trade_in_value=negotiation.trade_in_offered_value or Decimal('0'),
                purchase_price=Decimal(str(best_offer.get('purchase_price', 0))),
                monthly_payment=Decimal(str(best_offer.get('monthly_payment', 0))) if best_offer.get('monthly_payment') else None,
                duration_months=best_offer.get('duration_months'),
                total_cost=Decimal(str(best_offer.get('total_cost', 0))),
                warranty_months=best_offer.get('warranty_months', 12),
                maintenance_included=best_offer.get('maintenance_included', False),
                insurance_included=best_offer.get('insurance_included', False),
                justification=best_offer.get('reasoning', ''),
                confidence_score=Decimal(str(best_offer.get('confidence_score', 0))),
            )
            
            return offer
        
        raise ValueError("No offers could be generated")
    
    def _get_or_scrape_market_data(self, vehicle: Vehicle) -> Dict[str, Any]:
        """
        Get market data from cache or scrape if needed
        """
        
        # Check if we have recent market data
        market_data = MarketData.objects.filter(
            make=vehicle.make,
            model=vehicle.model,
            year=vehicle.year,
            fuel_type=vehicle.fuel_type
        ).first()
        
        if market_data and (datetime.now() - market_data.last_updated).days < 1:
            return self._market_data_to_dict(market_data)
        
        # Scrape market data
        scraped_data = self.scraper.aggregate_market_data(
            vehicle.make,
            vehicle.model,
            vehicle.year,
            vehicle.fuel_type
        )
        
        if scraped_data and 'aggregate' in scraped_data:
            agg = scraped_data['aggregate']
            
            market_data, created = MarketData.objects.update_or_create(
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                fuel_type=vehicle.fuel_type,
                defaults={
                    'average_price': Decimal(str(agg['average_price'])),
                    'price_min': Decimal(str(agg['min_price'])),
                    'price_max': Decimal(str(agg['max_price'])),
                    'listings_count': agg['listings_count'],
                    'mileage_average': 0,
                }
            )
            
            return self._market_data_to_dict(market_data)
        
        # Return empty data if scraping failed
        return {
            'average_price': vehicle.current_market_value,
            'min_price': vehicle.current_market_value * Decimal('0.9'),
            'max_price': vehicle.current_market_value * Decimal('1.1'),
            'listings_count': 0,
        }
    
    def _find_suitable_vehicle(self, client: Client) -> Optional[Vehicle]:
        """
        Find a suitable vehicle based on client preferences
        """
        
        query = Vehicle.objects.filter(in_stock=True)
        
        if client.preferred_fuel:
            query = query.filter(fuel_type=client.preferred_fuel)
        
        if client.preferred_transmission:
            query = query.filter(transmission=client.preferred_transmission)
        
        if client.budget_min and client.budget_max:
            query = query.filter(
                current_market_value__gte=client.budget_min,
                current_market_value__lte=client.budget_max
            )
        
        return query.first()
    
    def _vehicle_to_dict(self, vehicle: Optional[Vehicle]) -> Dict[str, Any]:
        """Convert vehicle model to dictionary"""
        if not vehicle:
            return {}
        
        return {
            'vin': vehicle.vin,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'mileage': vehicle.mileage,
            'fuel_type': vehicle.fuel_type,
            'power_hp': vehicle.power_hp,
            'current_market_value': float(vehicle.current_market_value),
            'estimated_value': float(vehicle.estimated_trade_in_value or 0),
            'condition': vehicle.condition,
            'retail_price': float(vehicle.current_market_value * Decimal('1.2')),
        }
    
    def _client_to_dict(self, client: Client) -> Dict[str, Any]:
        """Convert client model to dictionary"""
        return {
            'first_name': client.first_name,
            'last_name': client.last_name,
            'loyalty_score': float(client.loyalty_score),
            'risk_score': float(client.risk_score),
            'budget_min': float(client.budget_min or 0),
            'budget_max': float(client.budget_max or 0),
            'subscription_preference': client.subscription_preference,
        }
    
    def _offer_to_dict(self, offer: Offer) -> Dict[str, Any]:
        """Convert offer model to dictionary"""
        return {
            'offer_type': offer.offer_type,
            'trade_in_value': float(offer.trade_in_value),
            'purchase_price': float(offer.purchase_price or 0),
            'monthly_payment': float(offer.monthly_payment or 0),
            'duration_months': offer.duration_months,
            'total_cost': float(offer.total_cost),
            'warranty_months': offer.warranty_months,
            'maintenance_included': offer.maintenance_included,
            'insurance_included': offer.insurance_included,
            'confidence_score': float(offer.confidence_score),
        }
    
    def _market_data_to_dict(self, market_data: MarketData) -> Dict[str, Any]:
        """Convert market data model to dictionary"""
        return {
            'average_price': float(market_data.average_price),
            'price_min': float(market_data.price_min),
            'price_max': float(market_data.price_max),
            'listings_count': market_data.listings_count,
            'mileage_average': market_data.mileage_average,
        }
