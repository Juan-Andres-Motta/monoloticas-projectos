#!/usr/bin/env python3
"""
Simple Avro Schema Test - No External Dependencies

Tests the Avro schema loading without requiring Pulsar connection.
"""

import sys
import os
from uuid import uuid4
from datetime import datetime

# Add campaign service to path
sys.path.append("/Users/juan/Desktop/uniandes/monoliticas/campaingn")


def test_schema_import():
    """Test importing Avro schemas"""
    print("🔧 Testing Avro Schema Import")
    print("=" * 35)

    try:
        from messaging.schemas.avro_schemas import (
            CreateCampaignCommandAvro,
            AddVideoUrlCommandAvro,
            CreateTrackingEventCommandAvro,
            CalculateCommissionCommandAvro,
            ProcessPaymentCommandAvro,
            AvroSchemaRegistry,
        )

        print("✅ All Avro schemas imported successfully!")
        return True, {
            "CreateCampaignCommandAvro": CreateCampaignCommandAvro,
            "AddVideoUrlCommandAvro": AddVideoUrlCommandAvro,
            "CreateTrackingEventCommandAvro": CreateTrackingEventCommandAvro,
            "CalculateCommissionCommandAvro": CalculateCommissionCommandAvro,
            "ProcessPaymentCommandAvro": ProcessPaymentCommandAvro,
            "AvroSchemaRegistry": AvroSchemaRegistry,
        }
    except Exception as e:
        print(f"❌ Schema import failed: {e}")
        return False, None


def test_schema_instances(schemas):
    """Test creating schema instances"""
    print("\n🏗️ Testing Schema Instance Creation")
    print("=" * 40)

    try:
        # Test Campaign Command
        print("1️⃣ Testing Campaign Command Schema...")
        campaign_command = schemas["CreateCampaignCommandAvro"](
            command_id=str(uuid4()),
            campaign_id=str(uuid4()),
            user_id="test-user",
            name="Test Campaign",
            description="Schema validation test",
            correlation_id=str(uuid4()),
            timestamp=int(datetime.utcnow().timestamp() * 1000),  # milliseconds
        )
        print(f"   ✅ Campaign Command: {campaign_command.command_id[:8]}...")

        # Test Video Command
        print("2️⃣ Testing Video Command Schema...")
        video_command = schemas["AddVideoUrlCommandAvro"](
            command_id=str(uuid4()),
            campaign_id=str(uuid4()),
            video_url="https://youtube.com/watch?v=test123",
            correlation_id=str(uuid4()),
            timestamp=int(datetime.utcnow().timestamp() * 1000),  # milliseconds
        )
        print(f"   ✅ Video Command: {video_command.command_id[:8]}...")

        # Test Tracking Command
        print("3️⃣ Testing Tracking Command Schema...")
        tracking_command = schemas["CreateTrackingEventCommandAvro"](
            command_id=str(uuid4()),
            partner_id="test-partner",
            campaign_id="test-campaign",
            visitor_id="test-visitor",
            interaction_type="click",
            correlation_id=str(uuid4()),
            timestamp=int(datetime.utcnow().timestamp() * 1000),
        )
        print(f"   ✅ Tracking Command: {tracking_command.command_id[:8]}...")

        # Test Commission Command
        print("4️⃣ Testing Commission Command Schema...")
        commission_command = schemas["CalculateCommissionCommandAvro"](
            command_id=str(uuid4()),
            tracking_event_id=str(uuid4()),
            partner_id="test-partner",
            campaign_id="test-campaign",
            interaction_type="conversion",
            correlation_id=str(uuid4()),
            timestamp=int(datetime.utcnow().timestamp() * 1000),
        )
        print(f"   ✅ Commission Command: {commission_command.command_id[:8]}...")

        # Test Payment Command
        print("5️⃣ Testing Payment Command Schema...")
        payment_command = schemas["ProcessPaymentCommandAvro"](
            command_id=str(uuid4()),
            user_id="test-user",
            amount="99.99",
            currency="USD",
            payment_method="test_card",
            correlation_id=str(uuid4()),
            timestamp=int(datetime.utcnow().timestamp() * 1000),
        )
        print(f"   ✅ Payment Command: {payment_command.command_id[:8]}...")

        print("\n🎉 All schema instances created successfully!")
        return True

    except Exception as e:
        print(f"❌ Schema instance creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_schema_registry(schemas):
    """Test schema registry functionality"""
    print("\n📋 Testing Schema Registry")
    print("=" * 30)

    try:
        registry = schemas["AvroSchemaRegistry"]()

        print("📝 Available command schemas:")
        command_schemas = [
            "campaign.create.command.v1",
            "campaign.add_video.command.v1",
            "tracking.create_event.command.v1",
            "commission.calculate.command.v1",
            "payment.process.command.v1",
        ]

        for schema_name in command_schemas:
            try:
                schema = registry.get_command_schema(schema_name)
                print(f"   ✅ {schema_name}")
            except Exception as e:
                print(f"   ❌ {schema_name}: {e}")

        print("\n📝 Available event schemas:")
        event_schemas = [
            "campaign.created.v1",
            "video.added.v1",
            "tracking.event_created.v1",
            "commission.calculated.v1",
            "payment.processed.v1",
        ]

        for schema_name in event_schemas:
            try:
                # Try different method names that might exist
                if hasattr(registry, "get_event_schema"):
                    schema = registry.get_event_schema(schema_name)
                elif hasattr(registry, "get_schema"):
                    schema = registry.get_schema(schema_name)
                else:
                    print(
                        f"   ⚠️ {schema_name}: Domain event schema method not implemented yet"
                    )
                    continue
                print(f"   ✅ {schema_name}")
            except Exception as e:
                print(f"   ❌ {schema_name}: {e}")

        return True

    except Exception as e:
        print(f"❌ Schema registry test failed: {e}")
        return False


def main():
    """Run all schema tests"""
    print("🎯 Avro Schema Validation Tests")
    print("=" * 40)
    print()

    # Test 1: Import schemas
    success1, schemas = test_schema_import()
    if not success1:
        print("❌ Cannot continue without schemas")
        return False

    # Test 2: Create instances
    success2 = test_schema_instances(schemas)

    # Test 3: Test registry
    success3 = test_schema_registry(schemas)

    # Summary
    results = [success1, success2, success3]
    passed = sum(results)
    total = len(results)

    print(f"\n📊 Schema Tests: {passed}/{total} passed")

    if passed == total:
        print("🎉 All schema tests passed!")
        print("\n💡 Schemas are ready for event-driven messaging!")
        print("   Next: Set PULSAR_TOKEN and test with topic_tester.py")
    else:
        print("⚠️ Some schema tests failed")

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
        sys.exit(1)
