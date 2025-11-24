"""
Django management command to initialize sample data
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from negotiation.models import Vehicle, Client, User


class Command(BaseCommand):
    help = 'Initialize the database with sample vehicles and clients'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample vehicles...')
        
        # Sample vehicles for sale
        vehicles_data = [
            {
                'vin': 'VF7JU5N0005000001',
                'registration_number': 'AB-123-CD',
                'make': 'Peugeot',
                'model': '3008',
                'year': 2022,
                'version': 'Allure',
                'mileage': 15000,
                'fuel_type': 'diesel',
                'transmission': 'automatique',
                'power_hp': 160,
                'engine_cc': 1956,
                'original_purchase_price': Decimal('35000'),
                'current_market_value': Decimal('32000'),
                'estimated_trade_in_value': Decimal('30000'),
                'condition': 'excellent',
                'in_stock': True,
                'stock_location': 'Lot A, Place 1',
            },
            {
                'vin': 'VF7JU5N0005000002',
                'registration_number': 'AB-124-CD',
                'make': 'Renault',
                'model': 'Clio',
                'year': 2021,
                'version': 'Zen',
                'mileage': 28000,
                'fuel_type': 'essence',
                'transmission': 'manuelle',
                'power_hp': 110,
                'engine_cc': 1197,
                'original_purchase_price': Decimal('20000'),
                'current_market_value': Decimal('17500'),
                'estimated_trade_in_value': Decimal('16500'),
                'condition': 'bon',
                'in_stock': True,
                'stock_location': 'Lot B, Place 5',
            },
            {
                'vin': 'VF7JU5N0005000003',
                'registration_number': 'AB-125-CD',
                'make': 'Toyota',
                'model': 'Corolla',
                'year': 2023,
                'version': 'Hybride',
                'mileage': 5000,
                'fuel_type': 'hybride',
                'transmission': 'automatique',
                'power_hp': 122,
                'engine_cc': 1800,
                'original_purchase_price': Decimal('28000'),
                'current_market_value': Decimal('27000'),
                'estimated_trade_in_value': Decimal('25500'),
                'condition': 'excellent',
                'in_stock': True,
                'stock_location': 'Lot A, Place 3',
            },
            {
                'vin': 'VF7JU5N0005000004',
                'registration_number': 'AB-126-CD',
                'make': 'Tesla',
                'model': 'Model 3',
                'year': 2022,
                'version': 'Standard',
                'mileage': 12000,
                'fuel_type': 'electrique',
                'transmission': 'automatique',
                'power_hp': 285,
                'engine_cc': 0,
                'original_purchase_price': Decimal('45000'),
                'current_market_value': Decimal('42000'),
                'estimated_trade_in_value': Decimal('40000'),
                'condition': 'excellent',
                'in_stock': True,
                'stock_location': 'Lot C, Place 2',
            },
            {
                'vin': 'VF7JU5N0005000005',
                'registration_number': 'AB-127-CD',
                'make': 'Volkswagen',
                'model': 'Golf',
                'year': 2020,
                'version': 'GTI',
                'mileage': 45000,
                'fuel_type': 'essence',
                'transmission': 'manuelle',
                'power_hp': 245,
                'engine_cc': 1984,
                'original_purchase_price': Decimal('32000'),
                'current_market_value': Decimal('24000'),
                'estimated_trade_in_value': Decimal('22000'),
                'condition': 'moyen',
                'in_stock': True,
                'stock_location': 'Lot A, Place 4',
            },
        ]
        
        for vehicle_data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                vin=vehicle_data['vin'],
                defaults=vehicle_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created vehicle: {vehicle.year} {vehicle.make} {vehicle.model}')
                )
        
        self.stdout.write('Creating sample clients...')
        
        # Sample clients
        clients_data = [
            {
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'email': 'jean.dupont@example.com',
                'phone': '06 12 34 56 78',
                'address': '123 Rue de la Paix',
                'city': 'Paris',
                'postal_code': '75001',
                'preferred_fuel': 'diesel',
                'preferred_transmission': 'automatique',
                'budget_min': Decimal('25000'),
                'budget_max': Decimal('40000'),
                'subscription_preference': 'achat',
                'loyalty_score': Decimal('0.7'),
            },
            {
                'first_name': 'Marie',
                'last_name': 'Martin',
                'email': 'marie.martin@example.com',
                'phone': '06 87 65 43 21',
                'address': '456 Boulevard Saint-Germain',
                'city': 'Lyon',
                'postal_code': '69000',
                'preferred_fuel': 'essence',
                'preferred_transmission': 'manuelle',
                'budget_min': Decimal('15000'),
                'budget_max': Decimal('25000'),
                'subscription_preference': 'lld',
                'loyalty_score': Decimal('0.4'),
            },
            {
                'first_name': 'Pierre',
                'last_name': 'Bernard',
                'email': 'pierre.bernard@example.com',
                'phone': '06 11 22 33 44',
                'address': '789 Avenue des Champs',
                'city': 'Marseille',
                'postal_code': '13000',
                'preferred_fuel': 'electrique',
                'preferred_transmission': 'automatique',
                'budget_min': Decimal('40000'),
                'budget_max': Decimal('50000'),
                'subscription_preference': 'abonnement',
                'loyalty_score': Decimal('0.2'),
            },
        ]
        
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created client: {client.first_name} {client.last_name}')
                )
        
        self.stdout.write(self.style.SUCCESS('Sample data initialized successfully!'))
