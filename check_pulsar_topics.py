#!/usr/bin/env python3

import pulsar
import os
import json
from datetime import datetime


def check_pulsar_topics():
    """Check Pulsar topics for messages and statistics"""

    # Configuration
    SERVICE_URL = os.getenv(
        "PULSAR_SERVICE_URL",
        "pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651",
    )
    TOKEN = os.getenv("PULSAR_TOKEN", "YOUR_PULSAR_TOKEN")
    TENANT = os.getenv("PULSAR_TENANT", "miso-1-2025")
    NAMESPACE = os.getenv("PULSAR_NAMESPACE", "default")

    if TOKEN == "YOUR_PULSAR_TOKEN":
        print("❌ Please set PULSAR_TOKEN environment variable")
        return

    print("🔍 PULSAR TOPIC CHECKER")
    print("=" * 50)
    print(f"📡 Service URL: {SERVICE_URL}")
    print(f"🏢 Tenant: {TENANT}")
    print(f"📂 Namespace: {NAMESPACE}")
    print()

    try:
        # Create client
        client = pulsar.Client(
            service_url=SERVICE_URL, authentication=pulsar.AuthenticationToken(TOKEN)
        )

        # Topics to check
        topics = [
            f"persistent://{TENANT}/{NAMESPACE}/campaign-commands",
            f"persistent://{TENANT}/{NAMESPACE}/tracking-commands",
            f"persistent://{TENANT}/{NAMESPACE}/payment-commands",
            f"persistent://{TENANT}/{NAMESPACE}/campaign-events",
            f"persistent://{TENANT}/{NAMESPACE}/tracking-events",
            f"persistent://{TENANT}/{NAMESPACE}/payment-events",
        ]

        print("📊 TOPIC STATISTICS:")
        print("-" * 50)

        for topic in topics:
            try:
                # Create a reader to check messages
                reader = client.create_reader(topic, pulsar.MessageId.earliest)

                message_count = 0
                latest_messages = []

                print(f"\n🏷️  Topic: {topic}")

                # Read messages (limit to avoid infinite loop)
                try:
                    while reader.has_message_available() and message_count < 10:
                        msg = reader.read_next(timeout_millis=1000)
                        message_count += 1

                        # Parse message
                        try:
                            data = json.loads(msg.data().decode("utf-8"))
                            latest_messages.append(
                                {
                                    "message_id": str(msg.message_id()),
                                    "publish_time": msg.publish_timestamp(),
                                    "command_type": data.get("command_type", "unknown"),
                                    "command_id": data.get("command_id", "unknown"),
                                }
                            )
                        except:
                            latest_messages.append(
                                {
                                    "message_id": str(msg.message_id()),
                                    "publish_time": msg.publish_timestamp(),
                                    "data_size": len(msg.data()),
                                }
                            )

                except Exception as read_error:
                    if "TimeoutException" not in str(read_error):
                        print(f"   ⚠️  Read error: {read_error}")

                print(f"   📈 Messages found: {message_count}")

                if latest_messages:
                    print("   📋 Recent messages:")
                    for msg in latest_messages[-3:]:  # Show last 3
                        if "command_type" in msg:
                            print(
                                f"      • {msg['command_type']} ({msg['command_id'][:8]}...)"
                            )
                        else:
                            print(
                                f"      • Message {msg['message_id']} ({msg['data_size']} bytes)"
                            )

                reader.close()

            except Exception as topic_error:
                print(f"   ❌ Error accessing topic: {topic_error}")

        client.close()
        print(f"\n✅ Topic check completed at {datetime.now()}")

    except Exception as e:
        print(f"❌ Failed to connect to Pulsar: {e}")


if __name__ == "__main__":
    check_pulsar_topics()
