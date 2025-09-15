import os


class PulsarConfig:
    """Configuration for Pulsar connection - BFF Service"""

    # DataStax Astra Streaming configuration
    SERVICE_URL = os.getenv(
        "PULSAR_SERVICE_URL",
        "pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651",
    )

    TOKEN = os.getenv("PULSAR_TOKEN", "YOUR_PULSAR_TOKEN")

    # Topic configuration with fallbacks
    TENANT = os.getenv("PULSAR_TENANT", "miso-1-2025")
    NAMESPACE = os.getenv("PULSAR_NAMESPACE", "default")

    # BFF Command Topics (mapping to actual Pulsar topics)
    CAMPAIGN_ACCEPT_COMMANDS = f"persistent://{TENANT}/{NAMESPACE}/campaign-commands"
    CAMPAIGN_ACCEPT_RESPONSES = f"persistent://{TENANT}/{NAMESPACE}/campaign-events"

    EVIDENCE_UPLOAD_COMMANDS = f"persistent://{TENANT}/{NAMESPACE}/tracking-commands"
    EVIDENCE_UPLOAD_RESPONSES = f"persistent://{TENANT}/{NAMESPACE}/tracking-events"

    PAYMENT_REQUEST_COMMANDS = f"persistent://{TENANT}/{NAMESPACE}/payment-commands"
    PAYMENT_REQUEST_RESPONSES = f"persistent://{TENANT}/{NAMESPACE}/payment-events"

    # Consumer subscriptions
    BFF_RESPONSES_SUBSCRIPTION = "bff-responses-subscription"

    @classmethod
    def get_topic_options(cls, topic_name: str):
        """Get different topic configuration options to try"""
        return [
            f"persistent://{cls.TENANT}/{cls.NAMESPACE}/{topic_name}",
            f"persistent://public/default/{topic_name}",
            f"non-persistent://{cls.TENANT}/{cls.NAMESPACE}/{topic_name}",
            f'persistent://{cls.TENANT.replace("-", "_")}/{cls.NAMESPACE}/{topic_name}',
        ]

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

    @classmethod
    def get_all_command_topics(cls):
        """Get all command topics for publisher setup"""
        return [
            cls.CAMPAIGN_ACCEPT_COMMANDS,
            cls.EVIDENCE_UPLOAD_COMMANDS,
            cls.PAYMENT_REQUEST_COMMANDS,
        ]

    @classmethod
    def get_all_response_topics(cls):
        """Get all response topics for consumer setup"""
        return [
            cls.CAMPAIGN_ACCEPT_RESPONSES,
            cls.EVIDENCE_UPLOAD_RESPONSES,
            cls.PAYMENT_REQUEST_RESPONSES,
        ]
