#!/usr/bin/env python3
"""
Local Service Testing Script

This script tests the topic_tester functionality against the running HTTP services
to verify our message schemas and basic functionality work, even without Pulsar.
"""

import asyncio
import sys
import os
from uuid import uuid4
import json
import requests
from datetime import datetime


def test_http_services():
    """Test that HTTP services are running"""
    print("🌐 Testing HTTP Services")
    print("=" * 30)

    services = {
        "Campaign Service": "http://localhost:8002/health",
        "Tracking Service": "http://localhost:8003/health",
        "Commission Service": "http://localhost:8004/health",
        "Payment Service": "http://localhost:8005/health",
    }

    all_up = True

    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: UP")
            else:
                print(f"❌ {name}: DOWN (Status: {response.status_code})")
                all_up = False
        except Exception as e:
            print(f"❌ {name}: DOWN (Error: {str(e)[:50]}...)")
            all_up = False

    return all_up


def test_campaign_api():
    """Test campaign service HTTP API directly"""
    print("\n📋 Testing Campaign API")
    print("=" * 25)

    # Test creating a campaign via HTTP
    campaign_data = {
        "user_id": "test-user-001",
        "name": "Test Campaign via HTTP",
        "description": "Testing HTTP API before event-driven mode",
    }

    try:
        print("📤 Creating campaign via HTTP POST...")
        response = requests.post(
            "http://localhost:8002/campaigns", json=campaign_data, timeout=10
        )

        if response.status_code == 201:
            campaign = response.json()
            print(f"✅ Campaign created successfully!")
            print(f"   📍 ID: {campaign.get('id', 'N/A')}")
            print(f"   👤 User: {campaign.get('user_id', 'N/A')}")
            print(f"   📝 Name: {campaign.get('name', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to create campaign: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
            return False

    except Exception as e:
        print(f"❌ Campaign API test failed: {e}")
        return False


def test_avro_schema_loading():
    """Test that Avro schemas can be loaded without Pulsar connection"""
    print("\n🔧 Testing Avro Schema Loading")
    print("=" * 35)

    try:
        # Add campaign service to path
        sys.path.append("/Users/juan/Desktop/uniandes/monoliticas/campaingn")

        print("📋 Loading Avro schemas...")
        from messaging.schemas.avro_schemas import (
            CreateCampaignCommandAvro,
            AddVideoUrlCommandAvro,
            CreateTrackingEventCommandAvro,
            AvroSchemaRegistry,
        )

        print("✅ Avro schemas loaded successfully!")

        # Test creating schema instances
        print("🏗️ Testing schema instantiation...")

        campaign_command = CreateCampaignCommandAvro(
            command_id=str(uuid4()),
            campaign_id=str(uuid4()),
            user_id="test-user",
            name="Test Campaign",
            description="Schema test",
            correlation_id=str(uuid4()),
            timestamp=str(datetime.utcnow().isoformat()),
        )

        print("✅ Schema instances created successfully!")
        print(f"   📋 Campaign Command ID: {campaign_command.command_id}")
        print(f"   🔗 Correlation ID: {campaign_command.correlation_id}")

        return True

    except Exception as e:
        print(f"❌ Schema loading failed: {e}")
        print(f"   Error details: {str(e)}")
        return False


def test_topic_tester_import():
    """Test that topic_tester can be imported without errors"""
    print("\n🎯 Testing Topic Tester Import")
    print("=" * 35)

    try:
        print("📥 Importing topic_tester components...")

        # Import without running
        sys.path.append("/Users/juan/Desktop/uniandes/monoliticas")

        # Try to import the TopicTester class
        from topic_tester import TopicTester

        print("✅ TopicTester imported successfully!")

        # Test creating an instance
        print("🏗️ Creating TopicTester instance...")
        tester = TopicTester()
        print("✅ TopicTester instance created!")

        return True

    except Exception as e:
        print(f"❌ Topic tester import failed: {e}")
        print(f"   This is expected if Pulsar connection is required")
        return False


def run_all_tests():
    """Run all local tests"""
    print("🚀 Local Service Integration Tests")
    print("=" * 50)
    print()

    results = []

    # Test 1: HTTP Services
    results.append(("HTTP Services", test_http_services()))

    # Test 2: Campaign API
    results.append(("Campaign API", test_campaign_api()))

    # Test 3: Schema Loading
    results.append(("Avro Schemas", test_avro_schema_loading()))

    # Test 4: Topic Tester Import
    results.append(("Topic Tester", test_topic_tester_import()))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All local tests passed! Ready for event-driven testing.")
        print("\n💡 Next steps:")
        print("   1. Set PULSAR_TOKEN environment variable")
        print("   2. Run: python topic_tester.py campaign")
        print("   3. Check service logs for event processing")
    else:
        print("⚠️ Some tests failed. Fix issues before event-driven testing.")

    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)
