"""
Chat API using Gemini 2.0 Flash Lite with RAG
Complete workflow: User Query → Scrape Data → LLM Response
Moroccan Market Edition - All prices in MAD
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from negotiation.models import Vehicle, Client, Negotiation, Offer
from negotiation.rag import get_rag_service
from markdownify import markdownify as md
import json
import uuid


@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(APIView):
    """
    Chat endpoint using RAG pipeline
    POST /api/chat/
    {
        "message": "I want to buy a Tesla",
        "session_id": "optional-session-id"
    }
    """
    
    def post(self, request):
        """
        Handle user messages through RAG pipeline:
        1. Extract query
        2. Scrape relevant data
        3. Augment with Gemini
        4. Return response
        """
        try:
            data = request.data
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id', str(uuid.uuid4()))
            
            if not user_message:
                return Response(
                    {'error': 'Message cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get RAG service and process query
            rag_service = get_rag_service()
            result = rag_service.process_query(user_message, session_id)
            
            if result['success']:
                return Response({
                    'message': result['message'],
                    'session_id': session_id,
                    'data_sources': result['scraped_data'],
                    'timestamp': timezone.now().isoformat()
                })
            else:
                return Response(
                    {
                        'error': result.get('error', 'Unknown error'),
                        'session_id': session_id
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class PriceNegotiationView(APIView):
    """
    Price negotiation endpoint
    POST /api/negotiate/
    {
        "vehicle_id": 1,
        "proposed_price": 35000,
        "session_id": "session-id"
    }
    """
    
    def post(self, request):
        """Calculate fair counter-offer based on market data"""
        try:
            data = request.data
            vehicle_id = data.get('vehicle_id')
            proposed_price = float(data.get('proposed_price', 0))
            session_id = data.get('session_id', str(uuid.uuid4()))
            
            # Get vehicle
            vehicle = Vehicle.objects.get(id=vehicle_id)
            market_value = float(vehicle.estimated_value)
            
            # Calculate fair price range
            fair_min = market_value * 0.9
            fair_max = market_value * 1.1
            
            # Generate counter-offer using RAG
            rag_service = get_rag_service()
            negotiation_context = f"""
            Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}
            Market Value: €{market_value}
            Proposed Price: €{proposed_price}
            Fair Range: €{fair_min} - €{fair_max}
            """
            
            result = rag_service.process_query(
                f"Negotiate this: {negotiation_context}",
                session_id
            )
            
            return Response({
                'market_value': market_value,
                'proposed_price': proposed_price,
                'fair_min': fair_min,
                'fair_max': fair_max,
                'counter_offer': (fair_min + fair_max) / 2,
                'recommendation': result['message'],
                'session_id': session_id
            })
            
        except Vehicle.DoesNotExist:
            return Response(
                {'error': 'Vehicle not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Negotiation error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ClearSessionView(APIView):
    """Clear conversation history for a session"""
    
    def post(self, request):
        """POST /api/clear-session/"""
        try:
            session_id = request.data.get('session_id')
            if not session_id:
                return Response(
                    {'error': 'Session ID required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            rag_service = get_rag_service()
            rag_service.clear_session_history(session_id)
            
            return Response({
                'message': f'Session {session_id} cleared',
                'session_id': session_id
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
