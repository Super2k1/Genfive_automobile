#!/usr/bin/env python
"""
RAG System Test Script - Verify Gemini 2.0 Flash Lite Integration
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from negotiation.rag import get_rag_service
from negotiation.models import Vehicle
from dotenv import load_dotenv

# Load environment
load_dotenv()

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_setup():
    """Test environment and dependencies"""
    print_header("1️⃣  CHECKING SETUP")
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY: {api_key[:10]}...{api_key[-5:]}")
    else:
        print("❌ GEMINI_API_KEY: NOT SET - Edit .env file!")
        return False
    
    # Check database
    vehicle_count = Vehicle.objects.count()
    print(f"✅ Database: {vehicle_count} vehicles loaded")
    
    if vehicle_count == 0:
        print("⚠️  No vehicles in database!")
        print("   Run: python manage.py init_sample_data")
        return False
    
    # Check Gemini package
    try:
        import google.generativeai as genai
        print(f"✅ google-generativeai: Installed")
    except ImportError:
        print("❌ google-generativeai: Not installed")
        return False
    
    return True

def test_data_scraping():
    """Test RAG data scraping"""
    print_header("2️⃣  TESTING DATA SCRAPING")
    
    rag = get_rag_service()
    
    # Test vehicle scraping
    vehicles = rag.scrape_vehicle_data("Tesla")
    print(f"✅ Scraped {len(vehicles)} vehicles matching 'Tesla'")
    if vehicles:
        print(f"   - Sample: {vehicles[0]['make']} {vehicles[0]['model']} €{vehicles[0]['price']}")
    
    # Test market data
    market = rag.scrape_market_data()
    print(f"✅ Market Data:")
    print(f"   - Total vehicles: {market['total_vehicles']}")
    print(f"   - Avg price: €{market['average_price']:.0f}")
    print(f"   - Price range: €{market['min_price']:.0f} - €{market['max_price']:.0f}")
    
    return True

def test_rag_pipeline():
    """Test full RAG pipeline"""
    print_header("3️⃣  TESTING RAG PIPELINE")
    
    rag = get_rag_service()
    session_id = "test-session-123"
    
    # Test query
    test_queries = [
        "What cars do you have in inventory?",
        "What's the average price for a Tesla?",
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = rag.process_query(query, session_id)
        
        if result['success']:
            print(f"✅ Success!")
            print(f"   Response (first 100 chars): {result['message'][:100]}...")
            print(f"   Vehicles found: {result['scraped_data']['vehicles_found']}")
            print(f"   Market avg: €{result['scraped_data']['market_stats']['average_price']:.0f}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
            return False
    
    return True

def test_api_endpoint():
    """Test REST API endpoint"""
    print_header("4️⃣  TESTING API ENDPOINT")
    
    import requests
    import json
    
    url = "http://localhost:8000/api/chat/"
    
    payload = {
        "message": "What's the market price for a used car?",
        "session_id": "api-test-123"
    }
    
    try:
        print(f"📍 Testing: POST {url}")
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response (200 OK)")
            print(f"   Message: {data['message'][:100]}...")
            print(f"   Vehicles found: {data['data_sources']['vehicles_found']}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("   Make sure: python manage.py runserver is running")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_multi_turn():
    """Test multi-turn conversation"""
    print_header("5️⃣  TESTING MULTI-TURN CONVERSATION")
    
    rag = get_rag_service()
    session_id = "conversation-123"
    
    queries = [
        "I want to buy a car",
        "How much should I budget?",
        "What's a good first offer?"
    ]
    
    print(f"Session ID: {session_id}")
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Turn {i}: {query}")
        result = rag.process_query(query, session_id)
        
        if result['success']:
            print(f"✅ Response: {result['message'][:80]}...")
        else:
            print(f"❌ Error: {result['error']}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🚀 RAG SYSTEM TEST SUITE - Gemini 2.0 Flash Lite".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Setup", test_setup),
        ("Data Scraping", test_data_scraping),
        ("RAG Pipeline", test_rag_pipeline),
        ("API Endpoint", test_api_endpoint),
        ("Multi-Turn", test_multi_turn),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{'='*60}")
    print(f"  TOTAL: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! RAG System is ready to use!\n")
        print("Next Steps:")
        print("1. Open: http://localhost:8000")
        print("2. Try asking: 'What's the market price for a Tesla?'")
        print("3. Watch the RAG pipeline scrape data and respond!\n")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Check errors above.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
