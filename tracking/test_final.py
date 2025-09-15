#!/usr/bin/env python3
"""
Direct test with miso-1-2025 tenant
"""
import pulsar
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_miso_tenant():
    service_url = "pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651"
    token = os.getenv("PULSAR_TOKEN")

    print("🧪 Testing MISO-1-2025 Tenant")
    print("=" * 40)
    print(f"Service URL: {service_url}")
    print(f"Token length: {len(token)} characters")

    # Use miso-1-2025 tenant explicitly
    tenant = "miso-1-2025"
    namespace = "default"
    topic = f"persistent://{tenant}/{namespace}/tracking-events"

    print(f"Tenant: {tenant}")
    print(f"Namespace: {namespace}")
    print(f"Topic: {topic}")
    print()

    try:
        # Create client
        print("1. Creating Pulsar client...")
        client = pulsar.Client(
            service_url=service_url, authentication=pulsar.AuthenticationToken(token)
        )
        print("✅ Client created successfully")

        # Test producer
        print("2. Creating producer...")
        producer = client.create_producer(topic)
        print("✅ Producer created successfully")

        # Send a test message
        print("3. Sending test message...")
        message_data = "Hello from tracking service!"
        producer.send(message_data.encode("utf-8"))
        print("✅ Message sent successfully")

        # Test consumer
        print("4. Creating consumer...")
        consumer = client.subscribe(topic, subscription_name="test-sub")
        print("✅ Consumer created successfully")

        # Try to receive the message
        print("5. Trying to receive message...")
        try:
            msg = consumer.receive(timeout_millis=5000)
            print(f"✅ Message received: {msg.data().decode('utf-8')}")
            consumer.acknowledge(msg)
        except Exception as e:
            print(f"⚠️  Timeout waiting for message: {e}")

        # Cleanup
        print("6. Cleaning up...")
        producer.close()
        consumer.close()
        client.close()

        print("\n🎉 SUCCESS: DataStax Astra Streaming is working!")
        print("✅ Ready to start microservices with event streaming")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPossible solutions:")
        print("1. Verify the topic exists in DataStax console")
        print("2. Check token permissions for miso-1-2025 tenant")
        print("3. Try creating the topic manually first")
        return False


if __name__ == "__main__":
    test_miso_tenant()
