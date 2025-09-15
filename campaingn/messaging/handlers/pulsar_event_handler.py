"""
Pulsar Event Handler for Campaign Service
Integrates with the event-driven campaign handlers
"""

import asyncio
from campaign_event_handlers import start_event_driven_campaign_service


async def main():
    """Main entry point for campaign service event handler"""
    try:
        await start_event_driven_campaign_service()
    except KeyboardInterrupt:
        print("\n🛑 Campaign service event handler stopped")
    except Exception as e:
        print(f"❌ Error in campaign service event handler: {e}")


if __name__ == "__main__":
    asyncio.run(main())
