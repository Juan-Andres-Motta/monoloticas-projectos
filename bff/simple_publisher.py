#!/usr/bin/env python3
"""
Simple Pulsar Publisher for BFF Service
Publishes tracking events to Pulsar
"""

import json
import os
import pulsar
from uuid import uuid4
from datetime import datetime


class SimplePulsarPublisher:
    def __init__(self):
        self.client = None
        self.producers = {}  # Store multiple producers for different topics

    async def start(self):
        """Start Pulsar publisher"""
        try:
            # Pulsar configuration
            service_url = os.getenv("PULSAR_SERVICE_URL")
            token = os.getenv("PULSAR_TOKEN")
            tenant = os.getenv("PULSAR_TENANT", "miso-1-2025")
            namespace = os.getenv("PULSAR_NAMESPACE", "default")

            if not service_url or not token:
                raise ValueError("PULSAR_SERVICE_URL and PULSAR_TOKEN must be set")

            # Create client
            self.client = pulsar.Client(
                service_url, authentication=pulsar.AuthenticationToken(token)
            )

            # Create producers for different event types
            event_types = ["tracking-events", "campaign-events", "payment-events"]

            for event_type in event_types:
                # Try different topic variations
                topics = [
                    f"persistent://{tenant}/{namespace}/{event_type}",
                    f"persistent://public/default/{event_type}",
                    f"non-persistent://{tenant}/{namespace}/{event_type}",
                ]

                for topic in topics:
                    try:
                        print(f"📡 Attempting to create producer for: {topic}")
                        producer = self.client.create_producer(topic)
                        self.producers[event_type] = producer
                        print(f"✅ Successfully created producer for: {topic}")
                        break
                    except Exception as e:
                        print(f"❌ Failed to create producer for {topic}: {e}")
                        continue

                if event_type not in self.producers:
                    print(f"⚠️ Warning: Could not create producer for {event_type}")

        except Exception as e:
            print(f"❌ Failed to start publisher: {e}")
            raise

    async def publish_tracking_event(self, event_data):
        """Publish tracking event"""
        try:
            # Add event ID and timestamp
            event_data["tracking_event_id"] = str(uuid4())
            event_data["timestamp"] = datetime.utcnow().isoformat()
            event_data["event_type"] = "tracking_event.created"

            # Send message
            if "tracking-events" in self.producers:
                message_data = json.dumps(event_data).encode("utf-8")
                self.producers["tracking-events"].send(message_data)
                print(f"📤 Published tracking event: {event_data['tracking_event_id']}")
                return event_data["tracking_event_id"]
            else:
                raise Exception("Tracking events producer not available")

        except Exception as e:
            print(f"❌ Failed to publish tracking event: {e}")
            raise

    async def publish_campaign_event(self, event_data):
        """Publish campaign event"""
        try:
            # Add event ID and timestamp
            event_data["campaign_event_id"] = str(uuid4())
            event_data["timestamp"] = datetime.utcnow().isoformat()
            event_data["event_type"] = "campaign_event.created"

            # Send message
            if "campaign-events" in self.producers:
                message_data = json.dumps(event_data).encode("utf-8")
                self.producers["campaign-events"].send(message_data)
                print(f"📤 Published campaign event: {event_data['campaign_event_id']}")
                return event_data["campaign_event_id"]
            else:
                raise Exception("Campaign events producer not available")

        except Exception as e:
            print(f"❌ Failed to publish campaign event: {e}")
            raise

    async def publish_payment_event(self, event_data):
        """Publish payment event"""
        try:
            # Add event ID and timestamp
            if not event_data.get("payment_id"):
                event_data["payment_id"] = str(uuid4())
            event_data["payment_event_id"] = str(uuid4())
            event_data["timestamp"] = datetime.utcnow().isoformat()
            event_data["event_type"] = "payment_event.created"

            # Send message
            if "payment-events" in self.producers:
                message_data = json.dumps(event_data).encode("utf-8")
                self.producers["payment-events"].send(message_data)
                print(f"📤 Published payment event: {event_data['payment_event_id']}")
                return event_data["payment_event_id"]
            else:
                raise Exception("Payment events producer not available")

        except Exception as e:
            print(f"❌ Failed to publish payment event: {e}")
            raise

    async def stop(self):
        """Stop publisher"""
        for producer in self.producers.values():
            producer.close()
        if self.client:
            self.client.close()


# Global publisher instance
publisher = SimplePulsarPublisher()
