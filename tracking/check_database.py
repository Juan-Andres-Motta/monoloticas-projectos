#!/usr/bin/env python3
"""
Database verification script to check if tracking events are being persisted correctly.
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def check_database():
    """Check the database for tracking events"""
    try:
        # Get database URL
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://tracking_user:tracking_password@localhost:5432/trackingdb",
        )

        # Create engine and session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)

        with SessionLocal() as session:
            # Get table info (PostgreSQL style)
            result = session.execute(
                text(
                    """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'tracking_events'
                ORDER BY ordinal_position;
            """
                )
            )
            columns = result.fetchall()

            print("📋 Database schema:")
            for col in columns:
                print(f"   {col[0]} ({col[1]})")

            # Get count of records
            result = session.execute(text("SELECT COUNT(*) FROM tracking_events;"))
            count = result.scalar()
            print(f"\n📊 Total tracking events: {count}")

            if count > 0:
                # Get last 5 records
                result = session.execute(
                    text(
                        """
                    SELECT tracking_event_id, partner_id, campaign_id, visitor_id, 
                           interaction_type, source_url, destination_url, recorded_at, created_at
                    FROM tracking_events 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """
                    )
                )

                records = result.fetchall()
                print("\n🔍 Last 5 tracking events:")
                print("-" * 100)

                for record in records:
                    print(f"ID: {record[0]}")
                    print(
                        f"Partner: {record[1]} | Campaign: {record[2]} | Visitor: {record[3]}"
                    )
                    print(f"Type: {record[4]} | Created: {record[8]}")
                    print(f"Source: {record[5]}")
                    print(f"Destination: {record[6]}")
                    print("-" * 100)
            else:
                print("\n💡 No tracking events found. Try sending a POST request to:")
                print("   http://localhost:8000/api/v1/tracking/events")
                print("\n   Example payload:")
                example = {
                    "partner_id": "google-ads",
                    "campaign_id": "summer-sale-2025",
                    "visitor_id": "user123",
                    "interaction_type": "click",
                    "source_url": "https://google.com/ad",
                    "destination_url": "https://mystore.com/products",
                }
                print(json.dumps(example, indent=2))

    except Exception as e:
        print(f"❌ Database error: {e}")
        print(f"💡 Make sure PostgreSQL is running and accessible at: {database_url}")


if __name__ == "__main__":
    print("🔍 Checking PostgreSQL tracking service database...\n")
    check_database()
