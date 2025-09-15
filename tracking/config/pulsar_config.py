import os


class PulsarConfig:
    """Configuration for Pulsar connection"""

    # DataStax Astra Streaming configuration
    SERVICE_URL = os.getenv(
        "PULSAR_SERVICE_URL",
        "pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651",
    )

    TOKEN = os.getenv("PULSAR_TOKEN", "YOUR_PULSAR_TOKEN")

    # Topic configuration with fallbacks
    TENANT = os.getenv("PULSAR_TENANT", "miso-1-2025")
    NAMESPACE = os.getenv("PULSAR_NAMESPACE", "default")

    # Try different topic configurations
    @classmethod
    def get_topic_options(cls, topic_name: str):
        """Get different topic configuration options to try"""
        return [
            f"persistent://{cls.TENANT}/{cls.NAMESPACE}/{topic_name}",
            f"persistent://public/default/{topic_name}",
            f"non-persistent://{cls.TENANT}/{cls.NAMESPACE}/{topic_name}",
            f'persistent://{cls.TENANT.replace("-", "_")}/{cls.NAMESPACE}/{topic_name}',
        ]

    # Default topics (will be overridden by successful connection)
    TRACKING_EVENTS_TOPIC = f"persistent://{TENANT}/{NAMESPACE}/tracking-events"
    COMMISSIONS_TOPIC = f"persistent://{TENANT}/{NAMESPACE}/commissions"

    @classmethod
    def get_client_config(cls):
        """Get Pulsar client configuration"""
        import pulsar

        if cls.TOKEN == "YOUR_PULSAR_TOKEN":
            raise ValueError(
                "Please set PULSAR_TOKEN environment variable with your actual token"
            )

        return {
            "service_url": cls.SERVICE_URL,
            "authentication": pulsar.AuthenticationToken(cls.TOKEN),
        }
