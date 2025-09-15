#!/usr/bin/env python3

"""
DataStax Astra Streaming Connection Test Script
This script tests the Pulsar connection and helps troubleshoot issues.
"""

import os
import sys
import pulsar
from config.pulsar_config import PulsarConfig


def test_connection():
    """Test basic Pulsar connection"""
    print("🧪 Testing DataStax Astra Streaming Connection")
    print("-" * 50)

    try:
        # Load configuration
        print(f"Service URL: {PulsarConfig.SERVICE_URL}")
        print(f"Token length: {len(PulsarConfig.TOKEN)} characters")
        print(f"Topic: {PulsarConfig.TRACKING_EVENTS_TOPIC}")
        print()

        # Test 1: Basic client connection
        print("1. Testing client connection...")
        client_config = PulsarConfig.get_client_config()
        client = pulsar.Client(**client_config)
        print("✅ Client created successfully")

        # Test 2: List topics (requires admin permissions)
        print("\n2. Testing topic listing...")
        try:
            # This might fail if token doesn't have admin permissions
            admin = pulsar.Client(**client_config)
            print("✅ Admin client created")
        except Exception as e:
            print(f"⚠️  Admin operations not available: {e}")

        # Test 3: Create simple topic for testing
        print("\n3. Testing simple topic creation...")
        simple_topic = "persistent://miso-1-2025/default/test-topic"
        try:
            producer = client.create_producer(simple_topic)
            print(f"✅ Producer created for: {simple_topic}")
            producer.close()
        except Exception as e:
            print(f"❌ Failed to create producer for {simple_topic}: {e}")
            return False

        # Test 4: Test the actual tracking topic
        print("\n4. Testing tracking events topic...")
        try:
            producer = client.create_producer(PulsarConfig.TRACKING_EVENTS_TOPIC)
            print(f"✅ Producer created for: {PulsarConfig.TRACKING_EVENTS_TOPIC}")
            producer.close()
        except Exception as e:
            print(
                f"❌ Failed to create producer for {PulsarConfig.TRACKING_EVENTS_TOPIC}: {e}"
            )
            return False

        # Test 5: Test consumer
        print("\n5. Testing consumer...")
        try:
            consumer = client.subscribe(
                PulsarConfig.TRACKING_EVENTS_TOPIC,
                subscription_name="test-subscription",
            )
            print(f"✅ Consumer created for: {PulsarConfig.TRACKING_EVENTS_TOPIC}")
            consumer.close()
        except Exception as e:
            print(f"❌ Failed to create consumer: {e}")
            return False

        client.close()
        print("\n🎉 All tests passed! Connection is working correctly.")
        return True

    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check your PULSAR_TOKEN in .env file")
        print("2. Verify tenant/namespace exists: miso-1-2025/default")
        print("3. Check token permissions in DataStax Console")
        print("4. Try creating topics manually in DataStax Console first")
        return False


def suggest_fixes():
    """Suggest potential fixes based on common issues"""
    print("\n🔧 Common Solutions:")
    print("1. **Topic Auto-Creation**: Topics might need to be created manually")
    print("2. **Token Permissions**: Ensure token has producer/consumer permissions")
    print("3. **Namespace Configuration**: Verify miso-1-2025/default exists")
    print("4. **Alternative Topics**: Try with different topic names")
    print()
    print("💡 Try these alternatives:")

    alternatives = [
        "persistent://miso-1-2025/default/test",
        "non-persistent://miso-1-2025/default/tracking-events",
        "persistent://public/default/tracking-events",
    ]

    for alt in alternatives:
        print(f"   - {alt}")


if __name__ == "__main__":
    if not test_connection():
        suggest_fixes()
        sys.exit(1)
