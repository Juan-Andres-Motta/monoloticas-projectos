#!/usr/bin/env python3
"""
Event-Driven Architecture Demo
This script demonstrates how to send commands to microservices using Avro schemas and Pulsar.
"""

import asyncio
import sys
import os
from uuid import uuid4
from datetime import datetime

# Add the campaign service to the path to import avro schemas
sys.path.append("/Users/juan/Desktop/uniandes/monoliticas/campaingn")

from messaging.avro_publisher import avro_pulsar_publisher


async def demo_event_driven_architecture():
    """Demonstrate the complete event-driven workflow"""

    print("🎬 Event-Driven Microservices Demo")
    print("=" * 50)

    try:
        # Initialize publisher
        print("🚀 Starting Avro Pulsar Publisher...")
        await avro_pulsar_publisher.start()
        print("✅ Publisher ready!")

        # Demo 1: Create Campaign
        print("\n📋 Demo 1: Create Campaign")
        print("-" * 30)

        campaign_id = uuid4()
        correlation_id_1 = await avro_pulsar_publisher.send_create_campaign_command(
            campaign_id=campaign_id,
            user_id="demo-user-123",
            name="Event-Driven Demo Campaign",
            description="This campaign was created using Pulsar events with Avro schemas!",
        )

        print(f"✅ Create campaign command sent!")
        print(f"   📍 Campaign ID: {campaign_id}")
        print(f"   🔗 Correlation ID: {correlation_id_1}")

        # Wait for processing
        await asyncio.sleep(1)

        # Demo 2: Add Video URL
        print("\n🎥 Demo 2: Add Video URL to Campaign")
        print("-" * 40)

        correlation_id_2 = await avro_pulsar_publisher.send_add_video_url_command(
            campaign_id=campaign_id,
            video_url="https://youtube.com/watch?v=avro-pulsar-demo-123",
        )

        print(f"✅ Add video URL command sent!")
        print(f"   📍 Campaign ID: {campaign_id}")
        print(f"   🎥 Video URL: https://youtube.com/watch?v=avro-pulsar-demo-123")
        print(f"   🔗 Correlation ID: {correlation_id_2}")

        # Wait for processing
        await asyncio.sleep(1)

        # Demo 3: Create Tracking Event
        print("\n📊 Demo 3: Create Tracking Event")
        print("-" * 35)

        correlation_id_3 = (
            await avro_pulsar_publisher.send_create_tracking_event_command(
                partner_id="partner-abc-123",
                campaign_id=str(campaign_id),
                visitor_id="visitor-xyz-789",
                interaction_type="click",
            )
        )

        print(f"✅ Tracking event command sent!")
        print(f"   👤 Partner ID: partner-abc-123")
        print(f"   📍 Campaign ID: {campaign_id}")
        print(f"   👁️  Visitor ID: visitor-xyz-789")
        print(f"   🖱️  Interaction: click")
        print(f"   🔗 Correlation ID: {correlation_id_3}")

        # Wait for processing
        await asyncio.sleep(1)

        # Demo 4: Process Payment
        print("\n💳 Demo 4: Process Payment")
        print("-" * 25)

        correlation_id_4 = await avro_pulsar_publisher.send_process_payment_command(
            user_id="demo-user-123",
            amount=99.99,
            currency="USD",
            payment_method="credit_card",
            campaign_id=str(campaign_id),
        )

        print(f"✅ Process payment command sent!")
        print(f"   👤 User ID: demo-user-123")
        print(f"   💰 Amount: $99.99 USD")
        print(f"   💳 Method: credit_card")
        print(f"   📍 Campaign ID: {campaign_id}")
        print(f"   🔗 Correlation ID: {correlation_id_4}")

        # Summary
        print("\n🎯 Demo Complete!")
        print("=" * 50)
        print("📤 Commands sent to microservices:")
        print(f"   1. Create Campaign      → Correlation: {correlation_id_1}")
        print(f"   2. Add Video URL        → Correlation: {correlation_id_2}")
        print(f"   3. Create Tracking      → Correlation: {correlation_id_3}")
        print(f"   4. Process Payment      → Correlation: {correlation_id_4}")
        print()
        print("🔍 To see if commands were processed:")
        print("   1. Check the logs of each microservice")
        print("   2. Look for correlation IDs in the logs")
        print("   3. Verify database records were created")
        print()
        print("📡 Event Flow:")
        print(
            "   Client → Pulsar Topics → Microservices → Domain Events → Other Services"
        )

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise

    finally:
        # Cleanup
        await avro_pulsar_publisher.stop()
        print("🧹 Publisher stopped")


async def test_individual_commands():
    """Test individual command types"""

    print("🧪 Testing Individual Commands")
    print("=" * 35)

    try:
        await avro_pulsar_publisher.start()

        # Test 1: Campaign Creation
        print("\n🧪 Test 1: Campaign Creation Command")
        try:
            correlation_id = await avro_pulsar_publisher.send_create_campaign_command(
                campaign_id=uuid4(),
                user_id="test-user",
                name="Test Campaign",
                description="Test Description",
            )
            print(f"✅ SUCCESS - Correlation: {correlation_id}")
        except Exception as e:
            print(f"❌ FAILED - Error: {e}")

        # Test 2: Video URL Addition
        print("\n🧪 Test 2: Add Video URL Command")
        try:
            correlation_id = await avro_pulsar_publisher.send_add_video_url_command(
                campaign_id=uuid4(), video_url="https://example.com/video.mp4"
            )
            print(f"✅ SUCCESS - Correlation: {correlation_id}")
        except Exception as e:
            print(f"❌ FAILED - Error: {e}")

        # Test 3: Tracking Event
        print("\n🧪 Test 3: Tracking Event Command")
        try:
            correlation_id = (
                await avro_pulsar_publisher.send_create_tracking_event_command(
                    partner_id="test-partner",
                    campaign_id="test-campaign",
                    visitor_id="test-visitor",
                    interaction_type="view",
                )
            )
            print(f"✅ SUCCESS - Correlation: {correlation_id}")
        except Exception as e:
            print(f"❌ FAILED - Error: {e}")

        # Test 4: Commission Calculation
        print("\n🧪 Test 4: Commission Calculation Command")
        try:
            correlation_id = (
                await avro_pulsar_publisher.send_calculate_commission_command(
                    tracking_event_id=uuid4(),
                    partner_id="test-partner",
                    campaign_id="test-campaign",
                    interaction_type="conversion",
                )
            )
            print(f"✅ SUCCESS - Correlation: {correlation_id}")
        except Exception as e:
            print(f"❌ FAILED - Error: {e}")

        # Test 5: Payment Processing
        print("\n🧪 Test 5: Payment Processing Command")
        try:
            correlation_id = await avro_pulsar_publisher.send_process_payment_command(
                user_id="test-user",
                amount=50.00,
                currency="USD",
                payment_method="paypal",
            )
            print(f"✅ SUCCESS - Correlation: {correlation_id}")
        except Exception as e:
            print(f"❌ FAILED - Error: {e}")

        print("\n✅ Individual command tests completed!")

    except Exception as e:
        print(f"❌ Test setup failed: {e}")

    finally:
        await avro_pulsar_publisher.stop()


def print_usage():
    """Print usage instructions"""
    print("Event-Driven Architecture Demo")
    print("=" * 35)
    print()
    print("Usage:")
    print("  python test_event_driven.py demo     # Run complete demo")
    print("  python test_event_driven.py test     # Test individual commands")
    print("  python test_event_driven.py help     # Show this help")
    print()
    print("Prerequisites:")
    print("  1. Set up DataStax Astra Streaming credentials in .env")
    print("  2. Ensure PULSAR_TOKEN is configured")
    print("  3. Start microservices in event-driven mode:")
    print("     export CAMPAIGN_SERVICE_MODE=event")
    print("     python main_event_driven.py")
    print()
    print("Environment Variables:")
    print("  PULSAR_SERVICE_URL  - DataStax Astra Streaming URL")
    print("  PULSAR_TOKEN        - Your authentication token")
    print("  PULSAR_TENANT       - Tenant name (default: miso-1-2025)")
    print("  PULSAR_NAMESPACE    - Namespace (default: default)")


async def main():
    """Main entry point"""

    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command == "demo":
        await demo_event_driven_architecture()
    elif command == "test":
        await test_individual_commands()
    elif command == "help" or command == "--help":
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
