"""
Serializers for Django REST Framework
"""
from rest_framework import serializers
from negotiation.models import Vehicle, Client, Negotiation, Offer, NegotiationRound, MarketData


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model"""
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'vin', 'registration_number', 'make', 'model', 'year', 'version',
            'mileage', 'fuel_type', 'transmission', 'power_hp', 'engine_cc',
            'original_purchase_price', 'current_market_value', 'estimated_trade_in_value',
            'condition', 'in_stock', 'stock_location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model"""
    
    class Meta:
        model = Client
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'postal_code', 'trade_in_vehicle',
            'preferred_fuel', 'preferred_transmission', 'budget_min', 'budget_max',
            'subscription_preference', 'loyalty_score', 'risk_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'loyalty_score', 'risk_score', 'created_at', 'updated_at']


class MarketDataSerializer(serializers.ModelSerializer):
    """Serializer for MarketData model"""
    
    class Meta:
        model = MarketData
        fields = [
            'id', 'make', 'model', 'year', 'fuel_type',
            'average_price', 'price_min', 'price_max',
            'mileage_average', 'listings_count', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']


class OfferSerializer(serializers.ModelSerializer):
    """Serializer for Offer model"""
    
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    
    class Meta:
        model = Offer
        fields = [
            'id', 'negotiation', 'offer_type', 'vehicle', 'vehicle_details',
            'trade_in_value', 'purchase_price', 'monthly_payment', 'duration_months',
            'total_cost', 'warranty_months', 'maintenance_included', 'roadside_assistance',
            'insurance_included', 'justification', 'confidence_score', 'offer_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NegotiationRoundSerializer(serializers.ModelSerializer):
    """Serializer for NegotiationRound model"""
    
    class Meta:
        model = NegotiationRound
        fields = [
            'id', 'negotiation', 'round_number', 'agent_proposal',
            'agent_reasoning', 'client_feedback', 'client_counter_proposal',
            'round_status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NegotiationSerializer(serializers.ModelSerializer):
    """Serializer for Negotiation model"""
    
    client_details = ClientSerializer(source='client', read_only=True)
    trade_in_details = VehicleSerializer(source='trade_in_vehicle', read_only=True)
    target_details = VehicleSerializer(source='target_vehicle', read_only=True)
    offers_list = OfferSerializer(source='offers', many=True, read_only=True)
    rounds = NegotiationRoundSerializer(many=True, read_only=True)
    
    class Meta:
        model = Negotiation
        fields = [
            'id', 'client', 'client_details', 'trade_in_vehicle', 'trade_in_details',
            'target_vehicle', 'target_details', 'status', 'negotiation_rounds', 'max_rounds',
            'trade_in_offered_value', 'final_price', 'margin_achieved',
            'chosen_offer_type', 'agent_reasoning', 'market_analysis',
            'negotiation_history', 'offers_list', 'rounds',
            'started_at', 'ended_at', 'updated_at'
        ]
        read_only_fields = ['id', 'negotiation_rounds', 'started_at', 'ended_at', 'updated_at']


class NegotiationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Negotiation with all nested information"""
    
    client_details = ClientSerializer(source='client', read_only=True)
    trade_in_details = VehicleSerializer(source='trade_in_vehicle', read_only=True)
    target_details = VehicleSerializer(source='target_vehicle', read_only=True)
    offers = OfferSerializer(source='offers', many=True, read_only=True)
    negotiation_rounds = NegotiationRoundSerializer(source='rounds', many=True, read_only=True)
    
    class Meta:
        model = Negotiation
        fields = '__all__'
        read_only_fields = ['id', 'negotiation_rounds', 'started_at', 'ended_at', 'updated_at']


class InitiateNegotiationSerializer(serializers.Serializer):
    """Serializer for initiating a negotiation"""
    
    client_id = serializers.IntegerField()
    trade_in_vehicle_id = serializers.IntegerField(required=False, allow_null=True)
    target_vehicle_id = serializers.IntegerField(required=False, allow_null=True)
    business_margin_target = serializers.FloatField(default=0.15, min_value=0, max_value=1)


class ExecuteNegotiationRoundSerializer(serializers.Serializer):
    """Serializer for executing a negotiation round"""
    
    negotiation_id = serializers.IntegerField()
    client_feedback = serializers.CharField(required=False, allow_blank=True)
    proposed_counter_offer = serializers.JSONField(required=False, allow_null=True)
