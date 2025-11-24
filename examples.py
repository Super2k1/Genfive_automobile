#!/usr/bin/env python
"""
Example script demonstrating the autonomous negotiation platform
Run with: python manage.py shell < examples.py
"""

import os
import django
from decimal import Decimal
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from negotiation.models import Vehicle, Client, Negotiation, Offer
from negotiation.orchestration import NegotiationOrchestrator
from negotiation.agents import (
    MarketAnalysisAgent, TradeInEvaluationAgent, 
    OfferStructuringAgent, NegotiationAgent
)
from negotiation.scrapers import MarketDataScraper


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70 + "\n")


def example_1_market_analysis():
    """Example 1: Market Analysis"""
    print_header("Example 1: Market Analysis")
    
    # Get a vehicle
    vehicle = Vehicle.objects.filter(in_stock=True).first()
    if not vehicle:
        print("No vehicles in stock")
        return
    
    print(f"Analyzing market for: {vehicle.year} {vehicle.make} {vehicle.model}")
    
    # Create market analyzer agent
    analyzer = MarketAnalysisAgent()
    
    # Prepare vehicle data
    vehicle_data = {
        'make': vehicle.make,
        'model': vehicle.model,
        'year': vehicle.year,
        'mileage': vehicle.mileage,
        'fuel_type': vehicle.fuel_type,
        'condition': vehicle.condition,
    }
    
    # Mock market data
    market_data = {
        'average_price': float(vehicle.current_market_value),
        'min_price': float(vehicle.current_market_value * Decimal('0.9')),
        'max_price': float(vehicle.current_market_value * Decimal('1.1')),
        'listings_count': 25,
    }
    
    # Analyze market
    analysis = analyzer.analyze_market(vehicle_data, market_data)
    
    print("Market Analysis Results:")
    print("-" * 70)
    for key, value in analysis.items():
        print(f"  {key}: {value}")


def example_2_trade_in_evaluation():
    """Example 2: Trade-in Vehicle Evaluation"""
    print_header("Example 2: Trade-in Vehicle Evaluation")
    
    # Get a vehicle for trade-in
    vehicle = Vehicle.objects.filter(in_stock=False).first()
    if not vehicle:
        print("No trade-in vehicles available")
        return
    
    print(f"Evaluating trade-in: {vehicle.year} {vehicle.make} {vehicle.model}")
    print(f"Mileage: {vehicle.mileage} km")
    print(f"Condition: {vehicle.condition}")
    
    # Create evaluator
    evaluator = TradeInEvaluationAgent()
    
    # Prepare data
    vehicle_data = {
        'make': vehicle.make,
        'model': vehicle.model,
        'year': vehicle.year,
        'mileage': vehicle.mileage,
        'fuel_type': vehicle.fuel_type,
        'power_hp': vehicle.power_hp,
        'condition': vehicle.condition,
    }
    
    market_data = {
        'average_price': float(vehicle.current_market_value),
        'min_price': float(vehicle.current_market_value * Decimal('0.85')),
        'max_price': float(vehicle.current_market_value * Decimal('0.95')),
        'listings_count': 15,
    }
    
    # Evaluate
    evaluation = evaluator.evaluate_trade_in(vehicle_data, market_data, client_loyalty=0.7)
    
    print("\nTrade-in Evaluation Results:")
    print("-" * 70)
    for key, value in evaluation.items():
        print(f"  {key}: {value}")


def example_3_offer_structuring():
    """Example 3: Offer Structuring"""
    print_header("Example 3: Offer Structuring")
    
    # Get vehicles
    target_vehicle = Vehicle.objects.filter(in_stock=True).first()
    client = Client.objects.first()
    
    if not target_vehicle or not client:
        print("Missing vehicles or clients")
        return
    
    print(f"Target Vehicle: {target_vehicle.year} {target_vehicle.make} {target_vehicle.model}")
    print(f"Client Budget: €{client.budget_min} - €{client.budget_max}")
    print(f"Client Preference: {client.subscription_preference}")
    
    # Create offer structurer
    structurer = OfferStructuringAgent()
    
    # Prepare data
    vehicle_data = {
        'make': target_vehicle.make,
        'model': target_vehicle.model,
        'year': target_vehicle.year,
        'retail_price': float(target_vehicle.current_market_value * Decimal('1.2')),
        'market_value': float(target_vehicle.current_market_value),
    }
    
    offer_types = [client.subscription_preference] if client.subscription_preference != 'flexible' else ['achat', 'lld']
    
    business_objectives = {
        'target_margin': 0.15,
        'satisfaction_priority': 0.7,
    }
    
    client_budget = (
        float(client.budget_min or 25000),
        float(client.budget_max or 40000)
    )
    
    # Structure offers
    offers = structurer.structure_offer(
        vehicle_data,
        11000.0,  # Trade-in value
        offer_types,
        client_budget,
        business_objectives
    )
    
    print("\nStructured Offers:")
    print("-" * 70)
    if 'offers' in offers:
        for i, offer in enumerate(offers['offers'], 1):
            print(f"\nOffer {i}:")
            for key, value in offer.items():
                print(f"  {key}: {value}")


def example_4_complete_negotiation():
    """Example 4: Complete Negotiation Flow"""
    print_header("Example 4: Complete Negotiation Flow")
    
    # Get test data
    client = Client.objects.filter(subscription_preference='achat').first()
    trade_in = Vehicle.objects.filter(in_stock=False).first()
    target = Vehicle.objects.filter(in_stock=True).first()
    
    if not (client and trade_in and target):
        print("Missing test data")
        return
    
    print(f"Client: {client.first_name} {client.last_name}")
    print(f"Trade-in: {trade_in.year} {trade_in.make} {trade_in.model}")
    print(f"Target: {target.year} {target.make} {target.model}")
    
    # Initialize orchestrator
    orchestrator = NegotiationOrchestrator()
    
    # Initiate negotiation
    print("\n1. Initiating negotiation...")
    negotiation = orchestrator.initiate_negotiation(
        client_id=client.id,
        trade_in_vehicle_id=trade_in.id,
        target_vehicle_id=target.id,
        business_margin_target=0.15
    )
    
    print(f"   ✓ Negotiation {negotiation.id} created")
    print(f"   Status: {negotiation.status}")
    print(f"   Market Analysis: {bool(negotiation.market_analysis)}")
    
    # Get offers
    print("\n2. Checking generated offers...")
    offers = negotiation.offers.all()
    print(f"   ✓ {len(offers)} offer(s) generated")
    for offer in offers:
        print(f"   - {offer.offer_type}: €{offer.total_cost} (Confidence: {offer.confidence_score}%)")
    
    # Execute rounds
    print("\n3. Executing negotiation rounds...")
    
    client_feedbacks = [
        "L'offre de reprise est trop basse, j'espérais 11500€",
        "Mieux! Mais le prix d'achat me semble élevé",
        "Pouvez-vous inclure l'entretien pour 2 ans?",
    ]
    
    for i, feedback in enumerate(client_feedbacks, 1):
        print(f"\n   Round {i}:")
        print(f"   Client says: \"{feedback}\"")
        
        try:
            result = orchestrator.execute_negotiation_round(
                negotiation.id,
                feedback
            )
            
            if 'status' in result:
                if result['status'] == 'max_rounds_reached':
                    print(f"   ✓ Max rounds reached - negotiation concluded")
                    break
            
            print(f"   ✓ Round executed")
            if 'confidence' in result:
                print(f"   Confidence score: {result['confidence']}%")
            if 'should_continue' in result and not result['should_continue']:
                print(f"   ✓ Deal ready to close")
                break
        
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            break
    
    # Refresh and display final status
    negotiation.refresh_from_db()
    
    print("\n4. Final Results:")
    print("-" * 70)
    print(f"   Status: {negotiation.status}")
    print(f"   Rounds executed: {negotiation.negotiation_rounds}/{negotiation.max_rounds}")
    print(f"   Trade-in offered: €{negotiation.trade_in_offered_value}")
    print(f"   Final price: €{negotiation.final_price}")
    print(f"   Margin achieved: {negotiation.margin_achieved}%")
    
    # Show history
    if negotiation.rounds.exists():
        print(f"\n5. Negotiation History ({negotiation.rounds.count()} rounds):")
        print("-" * 70)
        for round_obj in negotiation.rounds.all():
            print(f"\n   Round {round_obj.round_number}:")
            print(f"   Status: {round_obj.round_status}")
            if round_obj.client_feedback:
                print(f"   Client feedback: \"{round_obj.client_feedback[:100]}...\"")


def example_5_scraping_demo():
    """Example 5: Market Data Scraping"""
    print_header("Example 5: Market Data Scraping")
    
    vehicle = Vehicle.objects.filter(in_stock=True).first()
    if not vehicle:
        print("No vehicles in stock")
        return
    
    print(f"Scraping market data for: {vehicle.year} {vehicle.make} {vehicle.model}")
    
    scraper = MarketDataScraper()
    
    print("Aggregating data from multiple sources...")
    print("Sources: LeBonCoin, Webmoteurs, Caradisiac, Argus")
    
    market_data = scraper.aggregate_market_data(
        vehicle.make,
        vehicle.model,
        vehicle.year,
        vehicle.fuel_type
    )
    
    print("\nMarket Data Results:")
    print("-" * 70)
    
    if 'sources' in market_data:
        print(f"\nData from {len(market_data.get('sources', {}))} sources:")
        for source, data in market_data.get('sources', {}).items():
            print(f"\n  {source}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"    {key}: {value}")
    
    if 'aggregate' in market_data:
        print(f"\nAggregated Results:")
        for key, value in market_data['aggregate'].items():
            print(f"  {key}: {value}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  PLATEFORME AGENTIQUE DE NÉGOCIATION AUTONOME")
    print("  Examples and Demonstrations")
    print("=" * 70)
    
    try:
        # Run examples
        example_1_market_analysis()
        example_2_trade_in_evaluation()
        example_3_offer_structuring()
        example_4_complete_negotiation()
        example_5_scraping_demo()
        
        print_header("Examples Completed Successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
