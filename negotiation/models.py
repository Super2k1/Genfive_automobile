"""
Django Models for Automobile Negotiation Platform
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json

class Vehicle(models.Model):
    """Model representing a vehicle available for purchase or trade-in"""
    
    FUEL_CHOICES = [
        ('essence', 'Essence'),
        ('diesel', 'Diesel'),
        ('hybride', 'Hybride'),
        ('electrique', 'Électrique'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manuelle', 'Manuelle'),
        ('automatique', 'Automatique'),
    ]
    
    # Basic information
    vin = models.CharField(max_length=17, unique=True)
    registration_number = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    version = models.CharField(max_length=100)
    
    # Technical specifications
    mileage = models.IntegerField(validators=[MinValueValidator(0)])
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    power_hp = models.IntegerField()
    engine_cc = models.IntegerField()
    
    # Valuation
    original_purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_market_value = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_trade_in_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('bon', 'Bon'),
        ('moyen', 'Moyen'),
        ('acceptable', 'Acceptable'),
    ]
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    
    # Inventory management
    in_stock = models.BooleanField(default=True)
    stock_location = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.vin})"


class Client(models.Model):
    """Model representing a client"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Address
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    
    # Trade-in vehicle information
    trade_in_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='trade_in_by')
    
    # Preferences
    preferred_fuel = models.CharField(max_length=20, choices=Vehicle.FUEL_CHOICES, blank=True)
    preferred_transmission = models.CharField(max_length=20, choices=Vehicle.TRANSMISSION_CHOICES, blank=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Subscription preferences
    SUBSCRIPTION_PREFERENCE_CHOICES = [
        ('achat', 'Achat'),
        ('lld', 'Location Longue Durée'),
        ('abonnement', 'Abonnement'),
        ('flexible', 'Flexible'),
    ]
    subscription_preference = models.CharField(max_length=20, choices=SUBSCRIPTION_PREFERENCE_CHOICES, default='flexible')
    
    # Client profile
    loyalty_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class MarketData(models.Model):
    """Market data for used vehicles (cached from scraping)"""
    
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    fuel_type = models.CharField(max_length=20)
    
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_min = models.DecimalField(max_digits=10, decimal_places=2)
    price_max = models.DecimalField(max_digits=10, decimal_places=2)
    
    mileage_average = models.IntegerField()
    listings_count = models.IntegerField()
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['make', 'model', 'year', 'fuel_type']
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.fuel_type})"


class Negotiation(models.Model):
    """Model representing a negotiation session"""
    
    STATUS_CHOICES = [
        ('initiated', 'Initiée'),
        ('in_progress', 'En cours'),
        ('pending_approval', 'En attente d\'approbation'),
        ('concluded', 'Conclue'),
        ('failed', 'Échouée'),
        ('cancelled', 'Annulée'),
    ]
    
    # Participants
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='negotiations')
    trade_in_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='trade_in_negotiations')
    target_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_negotiations')
    
    # Negotiation details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    negotiation_rounds = models.IntegerField(default=0)
    max_rounds = models.IntegerField(default=10)
    
    # Financial details
    trade_in_offered_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    margin_achieved = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Offer details
    chosen_offer_type = models.CharField(max_length=20, choices=Client.SUBSCRIPTION_PREFERENCE_CHOICES, null=True, blank=True)
    
    # AI Agent Data (JSON)
    agent_reasoning = models.JSONField(default=dict, blank=True)
    market_analysis = models.JSONField(default=dict, blank=True)
    negotiation_history = models.JSONField(default=list, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Negotiation {self.id} - {self.client} - {self.status}"


class Offer(models.Model):
    """Model representing an offer created by the AI agent"""
    
    OFFER_TYPE_CHOICES = [
        ('achat', 'Achat'),
        ('lld', 'Location Longue Durée'),
        ('abonnement', 'Abonnement'),
    ]
    
    negotiation = models.ForeignKey(Negotiation, on_delete=models.CASCADE, related_name='offers')
    
    # Offer details
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Financial terms
    trade_in_value = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monthly_payment = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    duration_months = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(84)])
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional benefits
    warranty_months = models.IntegerField(default=12)
    maintenance_included = models.BooleanField(default=False)
    roadside_assistance = models.BooleanField(default=False)
    insurance_included = models.BooleanField(default=False)
    
    # AI justification
    justification = models.TextField()
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Status
    OFFER_STATUS_CHOICES = [
        ('proposed', 'Proposée'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
        ('negotiating', 'En négociation'),
    ]
    offer_status = models.CharField(max_length=20, choices=OFFER_STATUS_CHOICES, default='proposed')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Offer {self.id} - {self.offer_type} - {self.offer_status}"


class NegotiationRound(models.Model):
    """Tracks each round of negotiation"""
    
    negotiation = models.ForeignKey(Negotiation, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField()
    
    # Agent decisions
    agent_proposal = models.JSONField()
    agent_reasoning = models.TextField()
    
    # Client response (simulated or actual)
    client_feedback = models.TextField(null=True, blank=True)
    client_counter_proposal = models.JSONField(null=True, blank=True)
    
    # Result
    round_status = models.CharField(max_length=20, choices=[
        ('ongoing', 'En cours'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
        ('counter', 'Contre-proposition'),
    ], default='ongoing')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['round_number']
    
    def __str__(self):
        return f"Round {self.round_number} - Negotiation {self.negotiation_id}"
