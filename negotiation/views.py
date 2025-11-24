"""
REST API Views for the automobile negotiation platform
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
import logging

from negotiation.models import Vehicle, Client, Negotiation, Offer, NegotiationRound
from negotiation.serializers import (
    VehicleSerializer, ClientSerializer, NegotiationSerializer,
    OfferSerializer, NegotiationDetailSerializer, InitiateNegotiationSerializer,
    ExecuteNegotiationRoundSerializer, NegotiationRoundSerializer, MarketDataSerializer
)
from negotiation.orchestration import NegotiationOrchestrator

logger = logging.getLogger(__name__)


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vehicle management
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['make', 'model', 'year', 'fuel_type', 'transmission', 'condition', 'in_stock']
    search_fields = ['make', 'model', 'vin', 'registration_number']
    ordering_fields = ['year', 'mileage', 'current_market_value', 'created_at']
    
    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """Get all vehicles in stock"""
        vehicles = Vehicle.objects.filter(in_stock=True)
        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search_by_criteria(self, request):
        """Search vehicles by specific criteria"""
        fuel = request.data.get('fuel_type')
        transmission = request.data.get('transmission')
        budget_min = request.data.get('budget_min')
        budget_max = request.data.get('budget_max')
        
        queryset = Vehicle.objects.filter(in_stock=True)
        
        if fuel:
            queryset = queryset.filter(fuel_type=fuel)
        if transmission:
            queryset = queryset.filter(transmission=transmission)
        if budget_min:
            queryset = queryset.filter(current_market_value__gte=budget_min)
        if budget_max:
            queryset = queryset.filter(current_market_value__lte=budget_max)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Client management
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'subscription_preference']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['loyalty_score', 'created_at']
    
    @action(detail=True, methods=['get'])
    def negotiations(self, request, pk=None):
        """Get all negotiations for a client"""
        client = self.get_object()
        negotiations = client.negotiations.all()
        serializer = NegotiationSerializer(negotiations, many=True)
        return Response(serializer.data)


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Offer management
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['offer_type', 'offer_status', 'negotiation']
    ordering_fields = ['total_cost', 'confidence_score', 'created_at']
    
    @action(detail=True, methods=['post'])
    def accept_offer(self, request, pk=None):
        """Accept an offer"""
        offer = self.get_object()
        offer.offer_status = 'accepted'
        offer.save()
        
        # Update negotiation
        negotiation = offer.negotiation
        negotiation.chosen_offer_type = offer.offer_type
        negotiation.final_price = offer.total_cost
        negotiation.status = 'concluded'
        negotiation.save()
        
        return Response({
            'status': 'offer_accepted',
            'offer_id': offer.id,
            'negotiation_id': negotiation.id
        })
    
    @action(detail=True, methods=['post'])
    def reject_offer(self, request, pk=None):
        """Reject an offer"""
        offer = self.get_object()
        offer.offer_status = 'rejected'
        offer.save()
        
        return Response({
            'status': 'offer_rejected',
            'offer_id': offer.id
        })


class NegotiationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Negotiation management
    """
    queryset = Negotiation.objects.all()
    serializer_class = NegotiationSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'client', 'chosen_offer_type']
    ordering_fields = ['started_at', 'margin_achieved', 'status']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NegotiationDetailSerializer
        return NegotiationSerializer
    
    @action(detail=True, methods=['post'])
    def execute_round(self, request, pk=None):
        """Execute a negotiation round"""
        negotiation = self.get_object()
        serializer = ExecuteNegotiationRoundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            orchestrator = NegotiationOrchestrator()
            result = orchestrator.execute_negotiation_round(
                negotiation.id,
                serializer.validated_data.get('client_feedback', '')
            )
            
            return Response(result)
        
        except Exception as e:
            logger.error(f"Error executing negotiation round: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get negotiation history"""
        negotiation = self.get_object()
        rounds = negotiation.rounds.all()
        serializer = NegotiationRoundSerializer(rounds, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """Get negotiation analysis and results"""
        negotiation = self.get_object()
        return Response({
            'negotiation_id': negotiation.id,
            'status': negotiation.status,
            'rounds_executed': negotiation.negotiation_rounds,
            'max_rounds': negotiation.max_rounds,
            'trade_in_offered_value': float(negotiation.trade_in_offered_value or 0),
            'final_price': float(negotiation.final_price or 0),
            'margin_achieved': float(negotiation.margin_achieved or 0),
            'market_analysis': negotiation.market_analysis,
            'agent_reasoning': negotiation.agent_reasoning,
            'duration_minutes': (
                (negotiation.ended_at - negotiation.started_at).total_seconds() / 60
                if negotiation.ended_at else None
            ),
        })


class InitiateNegotiationView(APIView):
    """
    API endpoint to initiate a new negotiation
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Initiate a new negotiation
        
        Request body:
        {
            "client_id": 1,
            "trade_in_vehicle_id": 5,
            "target_vehicle_id": 10,
            "business_margin_target": 0.15
        }
        """
        serializer = InitiateNegotiationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            orchestrator = NegotiationOrchestrator()
            negotiation = orchestrator.initiate_negotiation(
                client_id=serializer.validated_data['client_id'],
                trade_in_vehicle_id=serializer.validated_data.get('trade_in_vehicle_id'),
                target_vehicle_id=serializer.validated_data.get('target_vehicle_id'),
                business_margin_target=serializer.validated_data.get('business_margin_target', 0.15)
            )
            
            response_serializer = NegotiationDetailSerializer(negotiation)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Error initiating negotiation: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class NegotiationDetailView(APIView):
    """
    API endpoint for detailed negotiation information
    """
    permission_classes = [AllowAny]
    
    def get(self, request, negotiation_id):
        """Get detailed negotiation information"""
        negotiation = get_object_or_404(Negotiation, id=negotiation_id)
        serializer = NegotiationDetailSerializer(negotiation)
        return Response(serializer.data)
