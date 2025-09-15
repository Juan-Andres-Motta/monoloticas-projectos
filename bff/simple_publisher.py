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
        self.producer = None
        
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
                service_url,
                authentication=pulsar.AuthenticationToken(token)
            )
            
            # Try different topic variations
            topics = [
                f"persistent://{tenant}/{namespace}/tracking-events",
                f"persistent://public/default/tracking-events",
                f"non-persistent://{tenant}/{namespace}/tracking-events"
            ]
            
            for topic in topics:
                try:
                    print(f"📡 Attempting to create producer for: {topic}")
                    self.producer = self.client.create_producer(topic)
                    print(f"✅ Successfully created producer for: {topic}")
                    break
                except Exception as e:
                    print(f"❌ Failed to create producer for {topic}: {e}")
                    continue
            
            if not self.producer:
                raise Exception("Failed to create producer for any topic")
                
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
            message_data = json.dumps(event_data).encode('utf-8')
            self.producer.send(message_data)
            
            print(f"📤 Published tracking event: {event_data['tracking_event_id']}")
            return event_data["tracking_event_id"]
            
        except Exception as e:
            print(f"❌ Failed to publish event: {e}")
            raise
    
    async def stop(self):
        """Stop publisher"""
        if self.producer:
            self.producer.close()
        if self.client:
            self.client.close()

# Global publisher instance
publisher = SimplePulsarPublisher()
