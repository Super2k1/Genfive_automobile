"""
Application configuration for the negotiation app
"""
from django.apps import AppConfig


class NegotiationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'negotiation'
    verbose_name = 'Automobile Negotiation Platform'
