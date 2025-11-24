"""
URL Configuration for the automobile negotiation platform
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers
from negotiation.views import (
    VehicleViewSet, ClientViewSet, NegotiationViewSet, 
    OfferViewSet, NegotiationDetailView, InitiateNegotiationView
)
from negotiation.chat import ChatAPIView, PriceNegotiationView, ClearSessionView

router = routers.DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'negotiations', NegotiationViewSet)
router.register(r'offers', OfferViewSet)

urlpatterns = [
    path('', TemplateView.as_view(template_name='chat.html'), name='chat'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/chat/', ChatAPIView.as_view(), name='chat-api'),
    path('api/negotiate/', PriceNegotiationView.as_view(), name='negotiate'),
    path('api/clear-session/', ClearSessionView.as_view(), name='clear-session'),
    path('api/negotiations/<int:negotiation_id>/details/', NegotiationDetailView.as_view()),
    path('api/negotiations/initiate/', InitiateNegotiationView.as_view()),
    path('api-auth/', include('rest_framework.urls')),
]
