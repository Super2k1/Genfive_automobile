"""
AI Agents for autonomous negotiation
"""
import json
import logging
from decimal import Decimal
from typing import Dict, Any, List, Tuple
from datetime import datetime
import os

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

logger = logging.getLogger(__name__)


class AIAgent:
    """
    Base AI Agent class for negotiation
    """
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize the AI Agent"""
        self.model = model
        if Anthropic:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.client = Anthropic(api_key=api_key)
            else:
                self.client = None
                logger.warning("ANTHROPIC_API_KEY not set, agent will use mock mode")
        else:
            self.client = None
        self.conversation_history = []
    
    def _chat(self, message: str, system_prompt: str = "") -> str:
        """Send a message to Claude and get a response"""
        
        if not self.client:
            # Mock response for testing
            return self._mock_response(message)
        
        try:
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
        
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            return self._mock_response(message)
    
    def _mock_response(self, message: str) -> str:
        """Provide mock responses for testing"""
        return "Mock response - API not configured"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


class MarketAnalysisAgent(AIAgent):
    """
    Analyzes market data and provides insights
    """
    
    def analyze_market(self, vehicle_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market conditions for a vehicle
        
        Args:
            vehicle_data: Information about the vehicle
            market_data: Market price data
        
        Returns:
            Market analysis with recommendations
        """
        
        prompt = f"""
Analyze the following vehicle and market data to provide market analysis:

VEHICLE DATA:
{json.dumps(vehicle_data, indent=2, default=str)}

MARKET DATA:
{json.dumps(market_data, indent=2, default=str)}

Please provide:
1. Market demand assessment (high/medium/low)
2. Pricing positioning (above/at/below market)
3. Competitive advantage factors
4. Recommended positioning strategy
5. Risk factors
6. Opportunity assessment

Respond in JSON format.
"""
        
        system_prompt = """You are an expert automotive market analyst. Analyze vehicle market conditions
and provide strategic insights. Always respond with valid JSON."""
        
        response = self._chat(prompt, system_prompt)
        
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                analysis = {"raw_analysis": response}
        except json.JSONDecodeError:
            analysis = {"raw_analysis": response}
        
        return analysis


class TradeInEvaluationAgent(AIAgent):
    """
    Evaluates trade-in vehicles and proposes fair values
    """
    
    def evaluate_trade_in(self, vehicle: Dict[str, Any], market_data: Dict[str, Any], 
                         client_loyalty: float = 0.5) -> Dict[str, Any]:
        """
        Evaluate a trade-in vehicle and suggest fair trade-in value
        
        Args:
            vehicle: Trade-in vehicle data
            market_data: Market price data for similar vehicles
            client_loyalty: Client loyalty score (0-1)
        
        Returns:
            Trade-in evaluation with recommended values
        """
        
        prompt = f"""
You are an automotive valuation expert. Evaluate this trade-in vehicle and recommend a fair trade-in value.

TRADE-IN VEHICLE:
- Make: {vehicle.get('make')}
- Model: {vehicle.get('model')}
- Year: {vehicle.get('year')}
- Mileage: {vehicle.get('mileage')} km
- Condition: {vehicle.get('condition')}
- Fuel: {vehicle.get('fuel_type')}
- Power: {vehicle.get('power_hp')} HP

MARKET DATA:
Average Market Price: €{market_data.get('average_price', 0):,}
Price Range: €{market_data.get('min_price', 0):,} - €{market_data.get('max_price', 0):,}
Market Listings: {market_data.get('listings_count', 0)}

CLIENT LOYALTY SCORE: {client_loyalty} (0=new customer, 1=VIP)

Please provide:
1. Base trade-in value (considering market conditions)
2. Condition adjustment factors
3. Loyalty bonus (if applicable)
4. Final recommended trade-in offer
5. Reasoning for the valuation
6. Competitive positioning

Respond in JSON format with numerical values as numbers.
"""
        
        system_prompt = """You are an expert automotive valuation agent. Provide fair and competitive
trade-in valuations. Consider market conditions, vehicle condition, and client loyalty. Respond with valid JSON."""
        
        response = self._chat(prompt, system_prompt)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                evaluation = json.loads(json_str)
            else:
                evaluation = {"raw_evaluation": response}
        except json.JSONDecodeError:
            evaluation = {"raw_evaluation": response}
        
        return evaluation


class OfferStructuringAgent(AIAgent):
    """
    Structures purchase offers (purchase, LLD, subscription)
    """
    
    def structure_offer(self, 
                       vehicle: Dict[str, Any],
                       trade_in_value: float,
                       offer_types: List[str],
                       client_budget: Tuple[float, float],
                       business_objectives: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure complete offers for different subscription models
        
        Args:
            vehicle: Target vehicle data
            trade_in_value: Proposed trade-in value
            offer_types: Types of offers to structure ('achat', 'lld', 'abonnement')
            client_budget: Tuple of (min_budget, max_budget)
            business_objectives: Commercial targets (margin, volume, etc.)
        
        Returns:
            Structured offers for each requested type
        """
        
        prompt = f"""
You are a sales strategist expert in automotive pricing. Structure competitive offers for a customer.

TARGET VEHICLE:
- Make: {vehicle.get('make')}
- Model: {vehicle.get('model')}
- Year: {vehicle.get('year')}
- Retail Price: €{vehicle.get('retail_price', 0):,}
- Market Value: €{vehicle.get('market_value', 0):,}

TRADE-IN VALUE: €{trade_in_value:,}

CLIENT BUDGET: €{client_budget[0]:,} - €{client_budget[1]:,}

OFFER TYPES REQUESTED: {', '.join(offer_types)}

BUSINESS OBJECTIVES:
- Target Margin: {business_objectives.get('target_margin', 0)}%
- Customer Satisfaction Priority: {business_objectives.get('satisfaction_priority', 0.5)}

For each requested offer type, provide:
1. Financial structure (prices, monthly payments, total cost)
2. Terms and conditions
3. Included benefits (warranty, maintenance, insurance, etc.)
4. Confidence score for acceptance (0-100%)
5. Reasoning for the proposal
6. Risk assessment

Respond in JSON format with an array of offers.
"""
        
        system_prompt = """You are a professional automotive sales consultant. Create competitive, 
win-win offers that balance customer satisfaction with business profitability. Respond with valid JSON."""
        
        response = self._chat(prompt, system_prompt)
        
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                offers = json.loads(json_str)
            else:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    offers = [json.loads(json_str)]
                else:
                    offers = []
        except json.JSONDecodeError:
            offers = []
        
        return {"offers": offers, "raw_response": response}


class NegotiationAgent(AIAgent):
    """
    Orchestrates the negotiation process
    """
    
    def initiate_negotiation(self, 
                           client: Dict[str, Any],
                           trade_in_vehicle: Dict[str, Any],
                           market_analysis: Dict[str, Any],
                           business_objectives: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a negotiation session
        """
        
        prompt = f"""
You are an autonomous sales negotiation agent. A customer has initiated a negotiation for a vehicle trade-in and purchase.

CUSTOMER PROFILE:
- Name: {client.get('first_name')} {client.get('last_name')}
- Loyalty Score: {client.get('loyalty_score', 0)}
- Risk Score: {client.get('risk_score', 0)}
- Budget: €{client.get('budget_min', 0):,} - €{client.get('budget_max', 0):,}
- Preference: {client.get('subscription_preference', 'flexible')}

TRADE-IN VEHICLE:
- Make/Model: {trade_in_vehicle.get('make')} {trade_in_vehicle.get('model')}
- Year: {trade_in_vehicle.get('year')}
- Mileage: {trade_in_vehicle.get('mileage'):,} km
- Current Estimated Value: €{trade_in_vehicle.get('estimated_value', 0):,}

MARKET ANALYSIS: {json.dumps(market_analysis, default=str)[:500]}

BUSINESS OBJECTIVES:
- Target Margin: {business_objectives.get('target_margin', 0)}%
- Volume Target: {business_objectives.get('volume_target')}

Your tasks:
1. Assess the negotiation opportunity
2. Define your initial strategy
3. Propose opening positions for trade-in and new vehicle
4. Identify potential win-win solutions
5. Plan your negotiation approach

Respond in JSON format.
"""
        
        system_prompt = """You are an expert sales negotiation agent. You negotiate autonomously to achieve 
win-win outcomes that satisfy customers while meeting business targets. Be strategic, ethical, and customer-focused."""
        
        response = self._chat(prompt, system_prompt)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                strategy = json.loads(json_str)
            else:
                strategy = {"raw_strategy": response}
        except json.JSONDecodeError:
            strategy = {"raw_strategy": response}
        
        return strategy
    
    def process_round(self,
                     current_offer: Dict[str, Any],
                     client_feedback: str,
                     round_number: int,
                     max_rounds: int) -> Dict[str, Any]:
        """
        Process a negotiation round
        """
        
        prompt = f"""
You are in negotiation round {round_number} of {max_rounds}.

CURRENT OFFER:
{json.dumps(current_offer, indent=2, default=str)}

CUSTOMER FEEDBACK:
{client_feedback}

Please:
1. Analyze the customer's feedback
2. Assess if the deal is close or needs adjustment
3. Propose your response (accept, adjust offer, or negotiate further)
4. Calculate new terms if needed
5. Estimate probability of closing the deal
6. Provide reasoning

Respond in JSON format.
"""
        
        system_prompt = """You are an expert negotiator. Analyze customer feedback and adjust offers strategically.
Balance customer satisfaction with business profitability. Respond with valid JSON."""
        
        response = self._chat(prompt, system_prompt)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
            else:
                result = {"raw_result": response}
        except json.JSONDecodeError:
            result = {"raw_result": response}
        
        return result
