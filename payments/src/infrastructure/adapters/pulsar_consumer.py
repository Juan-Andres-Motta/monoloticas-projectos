import pulsar
import json
import asyncio
import logging
from pulsar.schema import AvroSchema
from src.application.handlers.register_payment_handler import RegisterPaymentHandler
from src.application.commands.register_payment_command import RegisterPaymentCommand
from src.domain.entities.payment import Payment
from .schemas import PaymentRecord

logger = logging.getLogger(__name__)


class PulsarConsumer:
    def __init__(
        self,
        handler: RegisterPaymentHandler,
        pulsar_service_url: str = "pulsar://localhost:6650",
        topic: str = "persistent://miso-1-2025/default/payments-request",
        token: str = "",
    ):
        self.handler = handler
        self.pulsar_service_url = pulsar_service_url
        self.topic = topic
        self.token = token
        self.client = None
        self.consumer = None

    async def start(self):
        logger.info(f"Connecting to Pulsar at {self.pulsar_service_url}")
        if self.token:
            self.client = pulsar.Client(
                self.pulsar_service_url,
                authentication=pulsar.AuthenticationToken(self.token),
            )
        else:
            self.client = pulsar.Client(self.pulsar_service_url)
        self.consumer = self.client.subscribe(
            self.topic, "payment-subscriber", schema=AvroSchema(PaymentRecord)
        )
        logger.info(f"Subscribed to topic: {self.topic}")

        while True:
            if asyncio.current_task().cancelled():
                break
            msg = None
            try:
                msg = self.consumer.receive()
                logger.info("Received payment request message from Pulsar")
                record = msg.value()
                data = {
                    "amount": record.amount,
                    "currency": record.currency,
                    "payment_method": record.payment_method,
                    "account_details": json.loads(record.account_details),
                    "user_id": record.user_id,
                }
                payment = Payment(**data)
                command = RegisterPaymentCommand(payment)
                await self.handler.handle(command)
                self.consumer.acknowledge(msg)
                logger.info(
                    f"Message processed successfully for user: {payment.user_id}"
                )
            except pulsar.Interrupted:
                logger.info("Consumer interrupted, shutting down")
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if msg:
                    self.consumer.negative_acknowledge(msg)

    def stop(self):
        logger.info("Stopping Pulsar consumer")
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()
        logger.info("Pulsar consumer stopped")
