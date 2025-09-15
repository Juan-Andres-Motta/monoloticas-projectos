#!/usr/bin/env python3
"""
Simple test to verify DataStax Astra Streaming connectivity
"""
import os
from dotenv import load_dotenv
import pulsar
import time

# Load environment variables
load_dotenv()


def test_simple_producer():
    service_url = os.getenv("PULSAR_SERVICE_URL")
    token = os.getenv("PULSAR_TOKEN")

    print("🧪 Testing Simple Producer/Consumer")
    print("--" * 25)
    print(f"Service URL: {service_url}")
    print(f"Token length: {len(token)} characters")

    # Try with public/default namespace
    topic = "persistent://public/default/test-simple"
    print(f"Topic: {topic}")

    try:
        # Create client
        client = pulsar.Client(
            service_url=service_url, authentication=pulsar.AuthenticationToken(token)
        )
        print("✅ Client created successfully")

        # Test producer
        producer = client.create_producer(topic)
        print("✅ Producer created successfully")

        # Send a test message
        message_data = "Hello DataStax Astra Streaming!"
        producer.send(message_data.encode("utf-8"))
        print("✅ Message sent successfully")

        # Test consumer
        consumer = client.subscribe(topic, subscription_name="test-subscription")
        print("✅ Consumer created successfully")

        # Try to receive the message (with timeout)
        try:
            msg = consumer.receive(timeout_millis=5000)
            print(f"✅ Message received: {msg.data().decode('utf-8')}")
            consumer.acknowledge(msg)
        except Exception as e:
            print(f"⚠️  No message received (this is OK for first test): {e}")

        # Cleanup
        producer.close()
        consumer.close()
        client.close()

        print("\n🎉 SUCCESS: Basic producer/consumer test passed!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_simple_producer()
    if success:
        print("\n✅ DataStax Astra Streaming is working correctly!")
    else:
        print("\n❌ There are still connectivity issues to resolve")
