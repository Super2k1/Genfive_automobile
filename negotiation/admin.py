"""
Admin configuration for automobile negotiation platform
"""
from django.contrib import admin
from negotiation.models import (
    Vehicle, Client, MarketData, Negotiation, Offer, NegotiationRound
)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vin', 'make', 'model', 'year', 'mileage', 'current_market_value', 'condition', 'in_stock']
    list_filter = ['make', 'fuel_type', 'transmission', 'condition', 'in_stock', 'year']
    search_fields = ['vin', 'registration_number', 'make', 'model']
    readonly_fields = ['vin', 'created_at', 'updated_at']
    fieldsets = (
        ('Informations de base', {
            'fields': ('vin', 'registration_number', 'make', 'model', 'year', 'version')
        }),
        ('Spécifications techniques', {
            'fields': ('mileage', 'fuel_type', 'transmission', 'power_hp', 'engine_cc')
        }),
        ('Valorisation', {
            'fields': ('original_purchase_price', 'current_market_value', 'estimated_trade_in_value')
        }),
        ('État et inventaire', {
            'fields': ('condition', 'in_stock', 'stock_location')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'loyalty_score', 'subscription_preference']
    list_filter = ['subscription_preference', 'city', 'loyalty_score']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'postal_code')
        }),
        ('Reprise', {
            'fields': ('trade_in_vehicle',)
        }),
        ('Préférences', {
            'fields': ('preferred_fuel', 'preferred_transmission', 'budget_min', 'budget_max', 'subscription_preference')
        }),
        ('Profil', {
            'fields': ('loyalty_score', 'risk_score')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    list_display = ['make', 'model', 'year', 'fuel_type', 'average_price', 'listings_count', 'last_updated']
    list_filter = ['make', 'fuel_type', 'year']
    search_fields = ['make', 'model']
    readonly_fields = ['last_updated']


@admin.register(Negotiation)
class NegotiationAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'status', 'negotiation_rounds', 'final_price', 'margin_achieved', 'started_at']
    list_filter = ['status', 'chosen_offer_type', 'started_at']
    search_fields = ['client__first_name', 'client__last_name', 'id']
    readonly_fields = ['started_at', 'ended_at', 'updated_at', 'negotiation_rounds']
    fieldsets = (
        ('Participants', {
            'fields': ('client', 'trade_in_vehicle', 'target_vehicle')
        }),
        ('Détails de la négociation', {
            'fields': ('status', 'negotiation_rounds', 'max_rounds')
        }),
        ('Conditions financières', {
            'fields': ('trade_in_offered_value', 'final_price', 'margin_achieved', 'chosen_offer_type')
        }),
        ('Données IA', {
            'fields': ('agent_reasoning', 'market_analysis', 'negotiation_history'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('started_at', 'ended_at', 'updated_at')
        }),
    )


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'negotiation', 'offer_type', 'vehicle', 'total_cost', 'confidence_score', 'offer_status']
    list_filter = ['offer_type', 'offer_status', 'created_at']
    search_fields = ['negotiation__id', 'vehicle__make']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Lien', {
            'fields': ('negotiation', 'vehicle')
        }),
        ('Type d\'offre', {
            'fields': ('offer_type',)
        }),
        ('Conditions financières', {
            'fields': ('trade_in_value', 'purchase_price', 'monthly_payment', 'duration_months', 'total_cost')
        }),
        ('Avantages inclus', {
            'fields': ('warranty_months', 'maintenance_included', 'roadside_assistance', 'insurance_included')
        }),
        ('Justification IA', {
            'fields': ('justification', 'confidence_score')
        }),
        ('Statut', {
            'fields': ('offer_status',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(NegotiationRound)
class NegotiationRoundAdmin(admin.ModelAdmin):
    list_display = ['round_number', 'negotiation', 'round_status', 'created_at']
    list_filter = ['round_status', 'created_at']
    search_fields = ['negotiation__id']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Informations de base', {
            'fields': ('negotiation', 'round_number', 'round_status')
        }),
        ('Proposition de l\'agent', {
            'fields': ('agent_proposal', 'agent_reasoning')
        }),
        ('Retour du client', {
            'fields': ('client_feedback', 'client_counter_proposal')
        }),
        ('Dates', {
            'fields': ('created_at',)
        }),
    )
