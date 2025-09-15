#!/usr/bin/env python3
"""
Individual Topic Testing Script

This script sends individual messages to specific Pulsar topics to test
each microservice independently. Perfect for debugging and verification.
"""

import asyncio
import sys
import os
from uuid import uuid4
from datetime import datetime

# Add the campaign service to the path
sys.path.append("/Users/juan/Desktop/uniandes/monoliticas/campaingn")

from messaging.avro_publisher import avro_pulsar_publisher


class TopicTester:
    """Individual topic testing utility"""

    def __init__(self):
        self.publisher_ready = False

    async def setup(self):
        """Initialize the publisher"""
        print("🔧 Initializing Pulsar publisher...")
        try:
            await avro_pulsar_publisher.start()
            self.publisher_ready = True
            print("✅ Publisher ready for testing")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize publisher: {e}")
            print("💡 Make sure your PULSAR_TOKEN is set in environment variables")
            return False

    async def cleanup(self):
        """Clean up resources"""
        if self.publisher_ready:
            await avro_pulsar_publisher.stop()
            print("🧹 Publisher stopped")

    async def test_campaign_service(self):
        """Test Campaign Service by sending create campaign command"""
        print("\n📋 Testing Campaign Service")
        print("-" * 40)
        print("📤 Sending: campaign.create.command.v1")

        campaign_id = uuid4()

        try:
            correlation_id = await avro_pulsar_publisher.send_create_campaign_command(
                campaign_id=campaign_id,
                user_id="test-user-001",
                name="Topic Test Campaign",
                description="Testing campaign service topic",
            )

            print(f"✅ Message sent successfully!")
            print(f"   📍 Campaign ID: {campaign_id}")
            print(f"   🔗 Correlation ID: {correlation_id}")
            print(f"   🎯 Topic: campaign-commands")
            print(f"   📋 Check Campaign Service logs for: {correlation_id}")

            return True

        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False

    async def test_campaign_add_video(self):
        """Test Campaign Service video addition"""
        print("\n🎥 Testing Campaign Service - Add Video")
        print("-" * 45)
        print("📤 Sending: campaign.add_video.command.v1")

        campaign_id = uuid4()

        try:
            correlation_id = await avro_pulsar_publisher.send_add_video_url_command(
                campaign_id=campaign_id,
                video_url="https://youtube.com/watch?v=topic-test-123",
            )

            print(f"✅ Message sent successfully!")
            print(f"   📍 Campaign ID: {campaign_id}")
            print(f"   🎥 Video URL: https://youtube.com/watch?v=topic-test-123")
            print(f"   🔗 Correlation ID: {correlation_id}")
            print(f"   🎯 Topic: campaign-commands")
            print(f"   📋 Check Campaign Service logs for: {correlation_id}")

            return True

        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False

    async def test_tracking_service(self):
        """Test Tracking Service by sending create tracking event command"""
        print("\n📊 Testing Tracking Service")
        print("-" * 35)
        print("📤 Sending: tracking.create_event.command.v1")

        try:
            correlation_id = (
                await avro_pulsar_publisher.send_create_tracking_event_command(
                    partner_id="test-partner-001",
                    campaign_id="test-campaign-001",
                    visitor_id="test-visitor-001",
                    interaction_type="click",
                )
            )

            print(f"✅ Message sent successfully!")
            print(f"   👤 Partner ID: test-partner-001")
            print(f"   📍 Campaign ID: test-campaign-001")
            print(f"   👁️  Visitor ID: test-visitor-001")
            print(f"   🖱️  Interaction: click")
            print(f"   🔗 Correlation ID: {correlation_id}")
            print(f"   🎯 Topic: tracking-commands")
            print(f"   📋 Check Tracking Service logs for: {correlation_id}")

            return True

        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False

    async def test_commission_service(self):
        """Test Commission Service by sending calculate commission command"""
        print("\n💰 Testing Commission Service")
        print("-" * 38)
        print("📤 Sending: commission.calculate.command.v1")

        tracking_event_id = uuid4()

        try:
            correlation_id = (
                await avro_pulsar_publisher.send_calculate_commission_command(
                    tracking_event_id=tracking_event_id,
                    partner_id="test-partner-001",
                    campaign_id="test-campaign-001",
                    interaction_type="conversion",
                )
            )

            print(f"✅ Message sent successfully!")
            print(f"   📊 Tracking Event ID: {tracking_event_id}")
            print(f"   👤 Partner ID: test-partner-001")
            print(f"   📍 Campaign ID: test-campaign-001")
            print(f"   💱 Interaction: conversion")
            print(f"   🔗 Correlation ID: {correlation_id}")
            print(f"   🎯 Topic: commission-commands")
            print(f"   📋 Check Commission Service logs for: {correlation_id}")

            return True

        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False

    async def test_payment_service(self):
        """Test Payment Service by sending process payment command"""
        print("\n💳 Testing Payment Service")
        print("-" * 32)
        print("📤 Sending: payment.process.command.v1")

        try:
            correlation_id = await avro_pulsar_publisher.send_process_payment_command(
                user_id="test-user-001",
                amount=99.99,
                currency="USD",
                payment_method="test_card",
            )

            print(f"✅ Message sent successfully!")
            print(f"   👤 User ID: test-user-001")
            print(f"   💰 Amount: $99.99 USD")
            print(f"   💳 Method: test_card")
            print(f"   🔗 Correlation ID: {correlation_id}")
            print(f"   🎯 Topic: payment-commands")
            print(f"   📋 Check Payment Service logs for: {correlation_id}")

            return True

        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False

    def print_service_check_instructions(self):
        """Print instructions for checking services"""
        print("\n" + "=" * 60)
        print("🔍 HOW TO VERIFY MESSAGES WERE RECEIVED")
        print("=" * 60)
        print()
        print("1. Check Service Logs:")
        print("   docker-compose logs -f campaign-service")
        print("   docker-compose logs -f tracking-service")
        print("   docker-compose logs -f commission-service")
        print("   docker-compose logs -f payment-service")
        print()
        print("2. Look for Correlation IDs in the logs")
        print("   Search for the correlation IDs printed above")
        print()
        print("3. Check DataStax Astra Streaming Console:")
        print("   - Go to console.datastax.com")
        print("   - Navigate to your Pulsar tenant")
        print("   - Check topics for message counts")
        print()
        print("4. Expected Topics in DataStax:")
        print("   persistent://miso-1-2025/default/campaign-commands")
        print("   persistent://miso-1-2025/default/tracking-commands")
        print("   persistent://miso-1-2025/default/commission-commands")
        print("   persistent://miso-1-2025/default/payment-commands")
        print()
        print("5. Service Status Check:")
        print("   docker-compose ps  # Check if services are running")
        print("   curl http://localhost:8002/health  # Campaign service")


async def test_all_topics():
    """Test all topics sequentially"""
    tester = TopicTester()

    if not await tester.setup():
        return

    print("🚀 Testing All Service Topics")
    print("=" * 50)

    results = []

    try:
        # Test each service
        results.append(await tester.test_campaign_service())
        await asyncio.sleep(1)

        results.append(await tester.test_campaign_add_video())
        await asyncio.sleep(1)

        results.append(await tester.test_tracking_service())
        await asyncio.sleep(1)

        results.append(await tester.test_commission_service())
        await asyncio.sleep(1)

        results.append(await tester.test_payment_service())

        # Summary
        successful = sum(results)
        total = len(results)

        print(f"\n📊 RESULTS: {successful}/{total} messages sent successfully")

        if successful == total:
            print("✅ All messages sent! Check service logs for processing.")
        else:
            print("⚠️  Some messages failed. Check configuration and retry.")

        tester.print_service_check_instructions()

    finally:
        await tester.cleanup()


async def test_single_topic(service_name: str):
    """Test a single service topic"""
    tester = TopicTester()

    if not await tester.setup():
        return

    print(f"🎯 Testing {service_name.title()} Service Topic")
    print("=" * 50)

    try:
        success = False

        if service_name == "campaign":
            success = await tester.test_campaign_service()
        elif service_name == "video":
            success = await tester.test_campaign_add_video()
        elif service_name == "tracking":
            success = await tester.test_tracking_service()
        elif service_name == "commission":
            success = await tester.test_commission_service()
        elif service_name == "payment":
            success = await tester.test_payment_service()
        else:
            print(f"❌ Unknown service: {service_name}")
            print("Available services: campaign, video, tracking, commission, payment")
            return

        if success:
            print(f"\n✅ {service_name.title()} service message sent successfully!")
            print(f"📋 Check {service_name} service logs to verify processing")
        else:
            print(f"\n❌ Failed to send message to {service_name} service")

        tester.print_service_check_instructions()

    finally:
        await tester.cleanup()


async def test_connection():
    """Test basic Pulsar connection"""
    print("🔌 Testing Pulsar Connection")
    print("=" * 35)

    tester = TopicTester()

    try:
        success = await tester.setup()
        if success:
            print("✅ Pulsar connection successful!")
            print("📡 Ready to send messages to topics")
        else:
            print("❌ Pulsar connection failed")
            print("💡 Check your configuration:")
            print("   - PULSAR_TOKEN environment variable")
            print("   - PULSAR_SERVICE_URL")
            print("   - Network connectivity to DataStax")

    finally:
        await tester.cleanup()


def print_usage():
    """Print usage instructions"""
    print("Individual Topic Testing Script")
    print("=" * 35)
    print()
    print("Usage:")
    print("  python topic_tester.py all                    # Test all services")
    print("  python topic_tester.py <service>             # Test single service")
    print("  python topic_tester.py connection            # Test Pulsar connection")
    print("  python topic_tester.py help                  # Show this help")
    print()
    print("Available Services:")
    print("  campaign     - Test campaign creation command")
    print("  video        - Test add video URL command")
    print("  tracking     - Test tracking event creation")
    print("  commission   - Test commission calculation")
    print("  payment      - Test payment processing")
    print()
    print("Examples:")
    print("  python topic_tester.py all")
    print("  python topic_tester.py campaign")
    print("  python topic_tester.py tracking")
    print()
    print("Prerequisites:")
    print("  1. Start your services:")
    print("     docker-compose up -d")
    print("  2. Set environment variables:")
    print("     export PULSAR_TOKEN=your_token")
    print("  3. Ensure services are in event-driven mode")


async def main():
    """Main entry point"""

    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    try:
        if command == "all":
            await test_all_topics()
        elif command == "connection":
            await test_connection()
        elif command in ["campaign", "video", "tracking", "commission", "payment"]:
            await test_single_topic(command)
        elif command == "help" or command == "--help":
            print_usage()
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()

    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
