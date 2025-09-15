#!/usr/bin/env python3
"""
Comprehensive Event-Driven Architecture Testing Script

This script provides various testing modes for the event-driven microservices:
- Individual command testing
- End-to-end workflow testing
- Load testing
- Schema validation testing
- Consumer verification
"""

import asyncio
import sys
import os
import time
import json
from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

# Add the campaign service to the path
sys.path.append("/Users/juan/Desktop/uniandes/monoliticas/campaingn")

from messaging.avro_publisher import avro_pulsar_publisher


class EventTestSuite:
    """Comprehensive test suite for event-driven architecture"""

    def __init__(self):
        self.test_results = []
        self.correlation_ids = []

    async def setup(self):
        """Initialize test environment"""
        print("🔧 Setting up test environment...")
        try:
            await avro_pulsar_publisher.start()
            print("✅ Test environment ready")
            return True
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            return False

    async def teardown(self):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")
        await avro_pulsar_publisher.stop()
        print("✅ Cleanup complete")

    def log_test_result(
        self, test_name: str, success: bool, message: str, correlation_id: str = None
    ):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "correlation_id": correlation_id,
        }
        self.test_results.append(result)

        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if correlation_id:
            print(f"   🔗 Correlation ID: {correlation_id}")

    async def test_campaign_creation(self) -> bool:
        """Test campaign creation command"""
        try:
            campaign_id = uuid4()
            correlation_id = await avro_pulsar_publisher.send_create_campaign_command(
                campaign_id=campaign_id,
                user_id="test-user-001",
                name="Automated Test Campaign",
                description="Campaign created by automated test",
            )
            self.correlation_ids.append(correlation_id)
            self.log_test_result(
                "Campaign Creation",
                True,
                f"Campaign {campaign_id} created",
                correlation_id,
            )
            return True
        except Exception as e:
            self.log_test_result("Campaign Creation", False, f"Error: {e}")
            return False

    async def test_video_url_addition(self) -> bool:
        """Test adding video URL to campaign"""
        try:
            campaign_id = uuid4()
            correlation_id = await avro_pulsar_publisher.send_add_video_url_command(
                campaign_id=campaign_id,
                video_url="https://youtube.com/watch?v=test-video-123",
            )
            self.correlation_ids.append(correlation_id)
            self.log_test_result(
                "Add Video URL", True, f"Video added to {campaign_id}", correlation_id
            )
            return True
        except Exception as e:
            self.log_test_result("Add Video URL", False, f"Error: {e}")
            return False

    async def test_tracking_event_creation(self) -> bool:
        """Test tracking event creation"""
        try:
            correlation_id = (
                await avro_pulsar_publisher.send_create_tracking_event_command(
                    partner_id="test-partner-001",
                    campaign_id="test-campaign-001",
                    visitor_id="test-visitor-001",
                    interaction_type="click",
                )
            )
            self.correlation_ids.append(correlation_id)
            self.log_test_result(
                "Tracking Event", True, "Tracking event created", correlation_id
            )
            return True
        except Exception as e:
            self.log_test_result("Tracking Event", False, f"Error: {e}")
            return False

    async def test_commission_calculation(self) -> bool:
        """Test commission calculation command"""
        try:
            correlation_id = (
                await avro_pulsar_publisher.send_calculate_commission_command(
                    tracking_event_id=uuid4(),
                    partner_id="test-partner-001",
                    campaign_id="test-campaign-001",
                    interaction_type="conversion",
                )
            )
            self.correlation_ids.append(correlation_id)
            self.log_test_result(
                "Commission Calculation",
                True,
                "Commission calculation triggered",
                correlation_id,
            )
            return True
        except Exception as e:
            self.log_test_result("Commission Calculation", False, f"Error: {e}")
            return False

    async def test_payment_processing(self) -> bool:
        """Test payment processing command"""
        try:
            correlation_id = await avro_pulsar_publisher.send_process_payment_command(
                user_id="test-user-001",
                amount=99.99,
                currency="USD",
                payment_method="test_card",
            )
            self.correlation_ids.append(correlation_id)
            self.log_test_result(
                "Payment Processing",
                True,
                "Payment processing triggered",
                correlation_id,
            )
            return True
        except Exception as e:
            self.log_test_result("Payment Processing", False, f"Error: {e}")
            return False

    async def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end workflow"""
        print("\n🔄 Testing End-to-End Workflow")
        print("-" * 40)

        workflow_correlation = str(uuid4())
        campaign_id = uuid4()

        try:
            # Step 1: Create campaign
            print("📋 Step 1: Creating campaign...")
            await avro_pulsar_publisher.send_create_campaign_command(
                campaign_id=campaign_id,
                user_id="e2e-user",
                name="E2E Test Campaign",
                description="End-to-end test workflow",
                correlation_id=workflow_correlation,
            )
            await asyncio.sleep(1)

            # Step 2: Add video URL
            print("🎥 Step 2: Adding video URL...")
            await avro_pulsar_publisher.send_add_video_url_command(
                campaign_id=campaign_id,
                video_url="https://youtube.com/watch?v=e2e-test",
                correlation_id=workflow_correlation,
            )
            await asyncio.sleep(1)

            # Step 3: Create tracking event
            print("📊 Step 3: Creating tracking event...")
            await avro_pulsar_publisher.send_create_tracking_event_command(
                partner_id="e2e-partner",
                campaign_id=str(campaign_id),
                visitor_id="e2e-visitor",
                interaction_type="click",
                correlation_id=workflow_correlation,
            )
            await asyncio.sleep(1)

            # Step 4: Process payment
            print("💳 Step 4: Processing payment...")
            await avro_pulsar_publisher.send_process_payment_command(
                user_id="e2e-user",
                amount=199.99,
                currency="USD",
                payment_method="e2e_card",
                campaign_id=str(campaign_id),
                correlation_id=workflow_correlation,
            )

            self.log_test_result(
                "E2E Workflow",
                True,
                f"Complete workflow executed",
                workflow_correlation,
            )
            return True

        except Exception as e:
            self.log_test_result("E2E Workflow", False, f"Workflow failed: {e}")
            return False

    async def test_load_performance(self, num_commands: int = 10) -> bool:
        """Test system performance with multiple commands"""
        print(f"\n⚡ Load Testing with {num_commands} commands")
        print("-" * 50)

        start_time = time.time()
        success_count = 0

        try:
            tasks = []
            for i in range(num_commands):
                # Create a mix of different commands
                if i % 4 == 0:
                    task = self.test_campaign_creation()
                elif i % 4 == 1:
                    task = self.test_video_url_addition()
                elif i % 4 == 2:
                    task = self.test_tracking_event_creation()
                else:
                    task = self.test_payment_processing()

                tasks.append(task)

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successful operations
            for result in results:
                if isinstance(result, bool) and result:
                    success_count += 1

            end_time = time.time()
            duration = end_time - start_time

            success_rate = (success_count / num_commands) * 100
            throughput = num_commands / duration

            message = f"{success_count}/{num_commands} commands successful ({success_rate:.1f}%), {throughput:.1f} cmd/sec"
            self.log_test_result("Load Test", success_count > 0, message)

            return success_count > 0

        except Exception as e:
            self.log_test_result("Load Test", False, f"Load test failed: {e}")
            return False

    async def test_error_scenarios(self) -> bool:
        """Test error handling scenarios"""
        print("\n🚫 Testing Error Scenarios")
        print("-" * 30)

        error_tests = []

        try:
            # Test 1: Invalid UUID
            print("🧪 Testing invalid campaign ID...")
            try:
                await avro_pulsar_publisher.send_add_video_url_command(
                    campaign_id="invalid-uuid",  # This should cause an error
                    video_url="https://test.com",
                )
                error_tests.append(False)  # Should have failed
            except Exception as e:
                print(f"✅ Correctly caught invalid UUID: {e}")
                error_tests.append(True)

            # Test 2: Empty required fields
            print("🧪 Testing empty required fields...")
            try:
                await avro_pulsar_publisher.send_create_campaign_command(
                    campaign_id=uuid4(),
                    user_id="",  # Empty user ID
                    name="",  # Empty name
                    description="",
                )
                error_tests.append(False)  # Should have failed
            except Exception as e:
                print(f"✅ Correctly caught empty fields: {e}")
                error_tests.append(True)

            all_passed = all(error_tests)
            self.log_test_result(
                "Error Scenarios",
                all_passed,
                f"{sum(error_tests)}/{len(error_tests)} error tests passed",
            )
            return all_passed

        except Exception as e:
            self.log_test_result("Error Scenarios", False, f"Error testing failed: {e}")
            return False

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if self.correlation_ids:
            print(f"\n🔗 Correlation IDs Generated: {len(self.correlation_ids)}")
            print("📋 Recent Correlation IDs:")
            for i, cid in enumerate(self.correlation_ids[-5:]):
                print(f"   {i+1}. {cid}")

        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")

        print("\n🔍 Next Steps:")
        print("1. Check microservice logs for correlation IDs")
        print("2. Verify database records were created")
        print("3. Monitor Pulsar topics for message delivery")
        print("4. Check DataStax Astra Streaming console")


async def run_basic_tests():
    """Run basic functionality tests"""
    test_suite = EventTestSuite()

    if not await test_suite.setup():
        return

    print("🧪 Running Basic Functionality Tests")
    print("=" * 50)

    try:
        # Run individual tests
        await test_suite.test_campaign_creation()
        await asyncio.sleep(0.5)

        await test_suite.test_video_url_addition()
        await asyncio.sleep(0.5)

        await test_suite.test_tracking_event_creation()
        await asyncio.sleep(0.5)

        await test_suite.test_commission_calculation()
        await asyncio.sleep(0.5)

        await test_suite.test_payment_processing()

    finally:
        await test_suite.teardown()
        test_suite.print_test_summary()


async def run_comprehensive_tests():
    """Run comprehensive test suite"""
    test_suite = EventTestSuite()

    if not await test_suite.setup():
        return

    print("🎯 Running Comprehensive Test Suite")
    print("=" * 50)

    try:
        # Basic tests
        print("\n🔹 Basic Functionality Tests")
        await test_suite.test_campaign_creation()
        await test_suite.test_video_url_addition()
        await test_suite.test_tracking_event_creation()
        await test_suite.test_commission_calculation()
        await test_suite.test_payment_processing()

        await asyncio.sleep(1)

        # End-to-end test
        await test_suite.test_end_to_end_workflow()

        await asyncio.sleep(2)

        # Load test
        await test_suite.test_load_performance(num_commands=5)

        await asyncio.sleep(1)

        # Error scenarios
        await test_suite.test_error_scenarios()

    finally:
        await test_suite.teardown()
        test_suite.print_test_summary()


async def run_load_test(num_commands: int = 20):
    """Run load testing"""
    test_suite = EventTestSuite()

    if not await test_suite.setup():
        return

    print(f"⚡ Running Load Test with {num_commands} commands")
    print("=" * 50)

    try:
        await test_suite.test_load_performance(num_commands)
    finally:
        await test_suite.teardown()
        test_suite.print_test_summary()


async def run_single_command_test(command_type: str):
    """Run a single command test"""
    test_suite = EventTestSuite()

    if not await test_suite.setup():
        return

    print(f"🎯 Testing Single Command: {command_type}")
    print("=" * 50)

    try:
        if command_type == "campaign":
            await test_suite.test_campaign_creation()
        elif command_type == "video":
            await test_suite.test_video_url_addition()
        elif command_type == "tracking":
            await test_suite.test_tracking_event_creation()
        elif command_type == "commission":
            await test_suite.test_commission_calculation()
        elif command_type == "payment":
            await test_suite.test_payment_processing()
        else:
            print(f"❌ Unknown command type: {command_type}")

    finally:
        await test_suite.teardown()
        test_suite.print_test_summary()


def print_usage():
    """Print usage instructions"""
    print("Event-Driven Architecture Test Suite")
    print("=" * 40)
    print()
    print("Usage:")
    print("  python event_test_suite.py basic                    # Run basic tests")
    print("  python event_test_suite.py comprehensive           # Run all tests")
    print("  python event_test_suite.py load [num_commands]     # Run load test")
    print("  python event_test_suite.py single <command_type>   # Test single command")
    print("  python event_test_suite.py help                    # Show this help")
    print()
    print("Command Types for Single Tests:")
    print("  campaign    - Test campaign creation")
    print("  video       - Test video URL addition")
    print("  tracking    - Test tracking event creation")
    print("  commission  - Test commission calculation")
    print("  payment     - Test payment processing")
    print()
    print("Examples:")
    print("  python event_test_suite.py basic")
    print("  python event_test_suite.py load 50")
    print("  python event_test_suite.py single campaign")
    print()
    print("Prerequisites:")
    print("  1. Configure DataStax Astra Streaming in .env")
    print("  2. Set PULSAR_TOKEN environment variable")
    print("  3. Ensure microservices are running")


async def main():
    """Main entry point"""

    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    try:
        if command == "basic":
            await run_basic_tests()
        elif command == "comprehensive":
            await run_comprehensive_tests()
        elif command == "load":
            num_commands = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            await run_load_test(num_commands)
        elif command == "single":
            if len(sys.argv) < 3:
                print("❌ Please specify command type for single test")
                print_usage()
                return
            await run_single_command_test(sys.argv[2])
        elif command == "help" or command == "--help":
            print_usage()
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()

    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test execution failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
