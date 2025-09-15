from seedwork.domain.domain_event_handler import DomainEventHandler
from seedwork.domain.domain_event import DomainEvent
from commission.domain.events.commission_calculated import CommissionCalculated


class CommissionNotificationHandler(DomainEventHandler):
    """Handles commission calculated events for notifications"""

    async def handle(self, event: DomainEvent) -> None:
        """Process commission calculated event"""
        if isinstance(event, CommissionCalculated):
            await self._send_commission_notification(event)

    async def _send_commission_notification(self, event: CommissionCalculated) -> None:
        """Send commission notification to partner"""
        print(f"💰 Commission Calculated Notification")
        print(f"   Commission ID: {event.commission_id}")
        print(f"   Partner: {event.partner_id}")
        print(f"   Campaign: {event.campaign_id}")
        print(f"   Amount: {event.commission_amount} {event.currency}")
        print(f"   Rate: {event.commission_rate * 100}%")
        print(f"   Interaction: {event.interaction_type}")
        print(f"   Tracking Event: {event.tracking_event_id}")

        # Here you would implement actual notification logic such as:
        # 1. Send email to partner
        # 2. Create webhook notification
        # 3. Update partner dashboard
        # 4. Log to audit system
        # 5. Update partner balance/earnings

        await self._update_partner_earnings(event)
        await self._log_commission_audit(event)

    async def _update_partner_earnings(self, event: CommissionCalculated) -> None:
        """Update partner earnings summary"""
        print(f"   → Updated earnings for partner {event.partner_id}")
        # This would update partner earnings aggregations

    async def _log_commission_audit(self, event: CommissionCalculated) -> None:
        """Log commission for audit purposes"""
        print(f"   → Logged commission audit record")
        # This would create audit log entries
