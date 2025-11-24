"""
Tests for the automobile negotiation platform
"""
from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from negotiation.models import Vehicle, Client, Negotiation, Offer
from negotiation.orchestration import NegotiationOrchestrator
from rest_framework.test import APIClient


class VehicleModelTest(TestCase):
    """Test Vehicle model"""
    
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            vin='VF7JU5N0005000001',
            registration_number='AB-123-CD',
            make='Peugeot',
            model='3008',
            year=2022,
            version='Allure',
            mileage=15000,
            fuel_type='diesel',
            transmission='automatique',
            power_hp=160,
            engine_cc=1956,
            current_market_value=Decimal('32000'),
            condition='excellent',
            in_stock=True,
        )
    
    def test_vehicle_creation(self):
        self.assertEqual(self.vehicle.make, 'Peugeot')
        self.assertEqual(self.vehicle.year, 2022)
        self.assertTrue(self.vehicle.in_stock)
    
    def test_vehicle_string_representation(self):
        expected = f"2022 Peugeot 3008 (VF7JU5N0005000001)"
        self.assertEqual(str(self.vehicle), expected)


class ClientModelTest(TestCase):
    """Test Client model"""
    
    def setUp(self):
        self.client = Client.objects.create(
            first_name='Jean',
            last_name='Dupont',
            email='jean@example.com',
            phone='0612345678',
            address='123 Rue de la Paix',
            city='Paris',
            postal_code='75001',
            budget_min=Decimal('25000'),
            budget_max=Decimal('40000'),
            subscription_preference='achat',
            loyalty_score=Decimal('0.7'),
        )
    
    def test_client_creation(self):
        self.assertEqual(self.client.first_name, 'Jean')
        self.assertEqual(self.client.city, 'Paris')
    
    def test_client_string_representation(self):
        expected = "Jean Dupont"
        self.assertEqual(str(self.client), expected)


class APIViewsTest(TestCase):
    """Test API views"""
    
    def setUp(self):
        self.client_api = APIClient()
        
        # Create test vehicle
        self.vehicle = Vehicle.objects.create(
            vin='VF7JU5N0005000001',
            registration_number='AB-123-CD',
            make='Peugeot',
            model='3008',
            year=2022,
            version='Allure',
            mileage=15000,
            fuel_type='diesel',
            transmission='automatique',
            power_hp=160,
            engine_cc=1956,
            current_market_value=Decimal('32000'),
            condition='excellent',
            in_stock=True,
        )
        
        # Create test client
        self.client_obj = Client.objects.create(
            first_name='Jean',
            last_name='Dupont',
            email='jean@example.com',
            phone='0612345678',
            address='123 Rue de la Paix',
            city='Paris',
            postal_code='75001',
            budget_min=Decimal('25000'),
            budget_max=Decimal('40000'),
            subscription_preference='achat',
        )
    
    def test_vehicle_list(self):
        response = self.client_api.get('/api/vehicles/')
        self.assertEqual(response.status_code, 200)
    
    def test_client_list(self):
        response = self.client_api.get('/api/clients/')
        self.assertEqual(response.status_code, 200)
    
    def test_vehicle_detail(self):
        response = self.client_api.get(f'/api/vehicles/{self.vehicle.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['make'], 'Peugeot')
    
    def test_client_detail(self):
        response = self.client_api.get(f'/api/clients/{self.client_obj.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Jean')


class NegotiationOrchestrationTest(TestCase):
    """Test negotiation orchestration"""
    
    def setUp(self):
        # Create test vehicles
        self.trade_in_vehicle = Vehicle.objects.create(
            vin='VF7JU5N0005000001',
            registration_number='AB-123-CD',
            make='Renault',
            model='Clio',
            year=2019,
            version='Zen',
            mileage=80000,
            fuel_type='essence',
            transmission='manuelle',
            power_hp=110,
            engine_cc=1197,
            current_market_value=Decimal('12000'),
            condition='bon',
            in_stock=False,
        )
        
        self.target_vehicle = Vehicle.objects.create(
            vin='VF7JU5N0005000002',
            registration_number='AB-124-CD',
            make='Peugeot',
            model='3008',
            year=2022,
            version='Allure',
            mileage=15000,
            fuel_type='diesel',
            transmission='automatique',
            power_hp=160,
            engine_cc=1956,
            current_market_value=Decimal('32000'),
            condition='excellent',
            in_stock=True,
        )
        
        # Create test client
        self.client = Client.objects.create(
            first_name='Jean',
            last_name='Dupont',
            email='jean@example.com',
            phone='0612345678',
            address='123 Rue de la Paix',
            city='Paris',
            postal_code='75001',
            trade_in_vehicle=self.trade_in_vehicle,
            budget_min=Decimal('25000'),
            budget_max=Decimal('40000'),
            subscription_preference='achat',
        )
    
    def test_initiate_negotiation(self):
        orchestrator = NegotiationOrchestrator()
        
        negotiation = orchestrator.initiate_negotiation(
            client_id=self.client.id,
            trade_in_vehicle_id=self.trade_in_vehicle.id,
            target_vehicle_id=self.target_vehicle.id,
        )
        
        self.assertIsNotNone(negotiation)
        self.assertEqual(negotiation.status, 'in_progress')
        self.assertEqual(negotiation.client.id, self.client.id)
