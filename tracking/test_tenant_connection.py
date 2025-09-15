#!/usr/bin/env python3
"""
Test with correct tenant miso-1-2025
"""
import os
from dotenv import load_dotenv
import pulsar
import time

# Load environment variables
load_dotenv()


def test_tenant_connection():
    service_url = os.getenv("PULSAR_SERVICE_URL")
    token = os.getenv("PULSAR_TOKEN")
    tenant = os.getenv("PULSAR_TENANT", "miso-1-2025")
    namespace = os.getenv("PULSAR_NAMESPACE", "default")

    print("🧪 Testing Tenant Connection")
    print("--" * 30)
    print(f"Service URL: {service_url}")
    print(f"Token length: {len(token)} characters")
    print(f"Tenant: {tenant}")
    print(f"Namespace: {namespace}")

    # Try with the tenant-specific topic
    topic = f"persistent://{tenant}/{namespace}/test-connection"
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
        message_data = f"Test message from tenant {tenant}"
        producer.send(message_data.encode("utf-8"))
        print("✅ Message sent successfully")

        # Test consumer
        consumer = client.subscribe(topic, subscription_name="test-subscription")
        print("✅ Consumer created successfully")

        # Try to receive the message
        try:
            msg = consumer.receive(timeout_millis=5000)
            print(f"✅ Message received: {msg.data().decode('utf-8')}")
            consumer.acknowledge(msg)
        except Exception as e:
            print(f"⚠️  No message received in timeout: {e}")

        # Cleanup
        producer.close()
        consumer.close()
        client.close()

        print(f"\n🎉 SUCCESS: Connection to tenant '{tenant}' works!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_tenant_connection()
    if success:
        print("\n✅ Ready to start the microservices!")
    else:
        print("\n❌ Still have issues to resolve")
