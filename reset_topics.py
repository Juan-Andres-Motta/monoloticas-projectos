#!/usr/bin/env python3
"""
Topic Reset Utility for DataStax Astra Streaming

This script helps reset topic schemas to resolve incompatibility issues.
Since we can't delete topics in DataStax Astra, we'll use new topic names.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TopicManager:
    """Manages topic names with versioning to avoid schema conflicts"""

    @staticmethod
    def get_versioned_topics():
        """Get topic names with version suffix to avoid schema conflicts"""
        timestamp = datetime.now().strftime("%H%M")
        version = f"v{timestamp}"

        return {
            "tracking_commands": f"persistent://miso-1-2025/default/tracking-commands-{version}",
            "campaign_commands": f"persistent://miso-1-2025/default/campaign-commands-{version}",
            "commission_commands": f"persistent://miso-1-2025/default/commission-commands-{version}",
            "payment_commands": f"persistent://miso-1-2025/default/payment-commands-{version}",
            # Domain events
            "tracking_events": f"persistent://miso-1-2025/default/tracking-events-{version}",
            "campaign_events": f"persistent://miso-1-2025/default/campaign-events-{version}",
            "commission_events": f"persistent://miso-1-2025/default/commission-events-{version}",
            "payment_events": f"persistent://miso-1-2025/default/payment-events-{version}",
        }

    @staticmethod
    def get_config_update():
        """Generate config update for new topic names"""
        topics = TopicManager.get_versioned_topics()

        config_lines = [
            "# Updated topic configuration with versioned names",
            "# Use these in your PulsarTopics class:",
            "",
            "TRACKING_COMMANDS_TOPIC = " + f'"{topics["tracking_commands"]}"',
            "CAMPAIGN_COMMANDS_TOPIC = " + f'"{topics["campaign_commands"]}"',
            "COMMISSION_COMMANDS_TOPIC = " + f'"{topics["commission_commands"]}"',
            "PAYMENT_COMMANDS_TOPIC = " + f'"{topics["payment_commands"]}"',
            "",
            "TRACKING_EVENTS_TOPIC = " + f'"{topics["tracking_events"]}"',
            "CAMPAIGN_EVENTS_TOPIC = " + f'"{topics["campaign_events"]}"',
            "COMMISSION_EVENTS_TOPIC = " + f'"{topics["commission_events"]}"',
            "PAYMENT_EVENTS_TOPIC = " + f'"{topics["payment_events"]}"',
        ]

        return "\n".join(config_lines)


def main():
    """Generate new topic configuration"""
    print("🔧 Topic Reset Utility")
    print("=" * 50)

    topics = TopicManager.get_versioned_topics()

    print("📡 New versioned topics:")
    for service, topic in topics.items():
        print(f"  {service}: {topic}")

    print("\n" + "=" * 50)
    print("📋 Configuration Update:")
    print(TopicManager.get_config_update())

    print("\n" + "=" * 50)
    print("✅ Copy the configuration above to your PulsarTopics class")
    print("   This will use fresh topics without schema conflicts")


if __name__ == "__main__":
    main()
