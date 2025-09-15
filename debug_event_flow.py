#!/usr/bin/env python3
"""
Debug Event Flow Script
This script helps debug why events are not flowing between services.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from uuid import uuid4

# Add paths for imports
sys.path.append("/Users/juan/Desktop/uniandes/monoliticas/tracking")
sys.path.append("/Users/juan/Desktop/uniandes/monoliticas/comission")

try:
    # Try to import Pulsar publisher from tracking service
    from messaging.pulsar_publisher import PulsarPublisher
    TRACKING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Could not import tracking Pulsar publisher: {e}")
    TRACKING_AVAILABLE = False

try:
    # Try to import commission consumer
    from infrastructure.messaging.pulsar_consumer import PulsarConsumer
    from config.container import Container
    COMMISSION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Could not import commission components: {e}")
    COMMISSION_AVAILABLE = False


class EventFlowDebugger:
    """Debug tool for event flow between services"""

    def __init__(self):
        self.tracking_publisher = None
        self.commission_consumer = None

    async def check_pulsar_config(self):
        """Check Pulsar configuration"""
        print("🔍 Checking Pulsar Configuration")
        print("=" * 40)

        # Check environment variables
        pulsar_url = os.getenv("PULSAR_SERVICE_URL")
        pulsar_token = os.getenv("PULSAR_TOKEN")
        pulsar_tenant = os.getenv("PULSAR_TENANT", "miso-1-2025")
        pulsar_namespace = os.getenv("PULSAR_NAMESPACE", "default")

        print(f"PULSAR_SERVICE_URL: {'✅ Set' if pulsar_url else '❌ Missing'}")
        print(f"PULSAR_TOKEN: {'✅ Set (' + pulsar_token[:20] + '...)' if pulsar_token and pulsar_token != 'YOUR_PULSAR_TOKEN' else '❌ Missing or default'}")
        print(f"PULSAR_TENANT: {pulsar_tenant}")
        print(f"PULSAR_NAMESPACE: {pulsar_namespace}")

        if not pulsar_url or not pulsar_token or pulsar_token == "YOUR_PULSAR_TOKEN":
            print("\n❌ Pulsar configuration is incomplete!")
            print("Please set the following environment variables:")
            print("  export PULSAR_SERVICE_URL='pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651'")
            print("  export PULSAR_TOKEN='your-actual-token-here'")
            return False

        print("\n✅ Pulsar configuration looks good!")
        return True

    async def test_tracking_publisher(self):
        """Test if tracking service can publish events"""
        if not TRACKING_AVAILABLE:
            print("❌ Tracking service publisher not available")
            return False

        print("\n🧪 Testing Tracking Service Publisher")
        print("=" * 40)

        try:
            self.tracking_publisher = PulsarPublisher()
            await self.tracking_publisher.start()
            print("✅ Tracking publisher started successfully")

            # Try to publish a test event
            test_event_id = uuid4()
            await self.tracking_publisher.publish_tracking_event(
                tracking_event_id=test_event_id,
                partner_id="test-partner-123",
                campaign_id="test-campaign-456",
                visitor_id="test-visitor-789",
                interaction_type="test_click"
            )
            print(f"✅ Test tracking event published: {test_event_id}")
            return True

        except Exception as e:
            print(f"❌ Tracking publisher failed: {e}")
            return False

    async def test_commission_consumer(self):
        """Test if commission service can consume events"""
        if not COMMISSION_AVAILABLE:
            print("❌ Commission service consumer not available")
            return False

        print("\n🧪 Testing Commission Service Consumer")
        print("=" * 40)

        try:
            # Initialize commission service container
            container = Container()
            command_bus = container.get("command_bus")
            
            self.commission_consumer = PulsarConsumer(command_bus)
            
            print("✅ Commission consumer initialized")
            
            # Note: We won't start the consumer loop here as it's blocking
            print("ℹ️  Consumer is ready to start (not starting loop in debug mode)")
            return True

        except Exception as e:
            print(f"❌ Commission consumer failed: {e}")
            return False

    async def test_end_to_end_flow(self):
        """Test complete end-to-end event flow"""
        print("\n🔄 Testing End-to-End Event Flow")
        print("=" * 40)

        if not TRACKING_AVAILABLE or not COMMISSION_AVAILABLE:
            print("❌ Cannot test end-to-end: services not available")
            return False

        try:
            # Publish an event from tracking
            if self.tracking_publisher:
                test_event_id = uuid4()
                print(f"📤 Publishing test event: {test_event_id}")
                
                await self.tracking_publisher.publish_tracking_event(
                    tracking_event_id=test_event_id,
                    partner_id="e2e-partner-123",
                    campaign_id="e2e-campaign-456", 
                    visitor_id="e2e-visitor-789",
                    interaction_type="e2e_conversion"
                )

                print("✅ Event published successfully")
                print("ℹ️  To verify consumption, check commission service logs")
                print("ℹ️  Or start commission service with: python main_event_driven.py")

                return True
            else:
                print("❌ Tracking publisher not available for E2E test")
                return False

        except Exception as e:
            print(f"❌ End-to-end test failed: {e}")
            return False

    async def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        if self.tracking_publisher:
            try:
                await self.tracking_publisher.stop()
                print("✅ Tracking publisher stopped")
            except Exception as e:
                print(f"⚠️  Error stopping tracking publisher: {e}")

    async def run_full_debug(self):
        """Run complete debug workflow"""
        print("🚀 Event Flow Debug Tool")
        print("=" * 50)
        print(f"Started at: {datetime.now()}")
        print()

        try:
            # Step 1: Check configuration
            config_ok = await self.check_pulsar_config()
            if not config_ok:
                return

            # Step 2: Test tracking publisher
            tracking_ok = await self.test_tracking_publisher()

            # Step 3: Test commission consumer
            commission_ok = await self.test_commission_consumer()

            # Step 4: Test end-to-end (if both services available)
            if tracking_ok and commission_ok:
                await self.test_end_to_end_flow()

            # Summary
            print("\n📊 Debug Summary")
            print("=" * 20)
            print(f"Pulsar Config: {'✅ OK' if config_ok else '❌ Failed'}")
            print(f"Tracking Publisher: {'✅ OK' if tracking_ok else '❌ Failed'}")
            print(f"Commission Consumer: {'✅ OK' if commission_ok else '❌ Failed'}")

            if config_ok and tracking_ok and commission_ok:
                print("\n🎉 All components working!")
                print("💡 To test full flow:")
                print("   1. Start commission service: cd comission && python main_event_driven.py")
                print("   2. Make HTTP request to tracking service")
                print("   3. Check commission service logs for received events")
            else:
                print("\n⚠️  Issues found - see details above")

        except Exception as e:
            print(f"❌ Debug run failed: {e}")
        finally:
            await self.cleanup()


async def main():
    """Main function"""
    debugger = EventFlowDebugger()
    await debugger.run_full_debug()


if __name__ == "__main__":
    asyncio.run(main())
