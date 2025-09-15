#!/bin/bash

# Test script for Commission Service integration

echo "🧪 Testing Commission Service Integration"

TRACKING_URL="http://localhost:8000"
COMMISSION_URL="http://localhost:8001"

echo ""
echo "1. Testing service health checks..."

# Test tracking service health
echo "📋 Tracking Service Health:"
curl -s "$TRACKING_URL/api/v1/tracking/health" | jq '.' 2>/dev/null || curl -s "$TRACKING_URL/api/v1/tracking/health"

echo ""
echo "💰 Commission Service Health:"
curl -s "$COMMISSION_URL/api/v1/commissions/health" | jq '.' 2>/dev/null || curl -s "$COMMISSION_URL/api/v1/commissions/health"

echo ""
echo ""
echo "2. Creating tracking event (should trigger commission automatically)..."

# Create a tracking event
TRACKING_RESPONSE=$(curl -s -X POST "$TRACKING_URL/api/v1/tracking/events" \
  -H "Content-Type: application/json" \
  -d '{
    "partner_id": "partner_premium_1",
    "campaign_id": "campaign_test_123",
    "visitor_id": "visitor_test_456",
    "interaction_type": "click",
    "source_url": "https://example.com",
    "destination_url": "https://destination.com"
  }')

echo "📤 Tracking Event Created:"
echo "$TRACKING_RESPONSE" | jq '.' 2>/dev/null || echo "$TRACKING_RESPONSE"

echo ""
echo "⏳ Waiting 5 seconds for commission processing..."
sleep 5

echo ""
echo "3. Checking generated commissions..."

# Check commissions for the partner
echo "💰 Partner Commissions:"
curl -s "$COMMISSION_URL/api/v1/commissions/partner/partner_premium_1" | jq '.' 2>/dev/null || curl -s "$COMMISSION_URL/api/v1/commissions/partner/partner_premium_1"

echo ""
echo ""
echo "4. Manual commission calculation test..."

# Manual commission calculation
COMMISSION_RESPONSE=$(curl -s -X POST "$COMMISSION_URL/api/v1/commissions/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "tracking_event_id": "550e8400-e29b-41d4-a716-446655440000",
    "partner_id": "partner_test_2", 
    "campaign_id": "campaign_manual_test",
    "visitor_id": "visitor_manual_test",
    "interaction_type": "engagement"
  }')

echo "📤 Manual Commission Calculation:"
echo "$COMMISSION_RESPONSE" | jq '.' 2>/dev/null || echo "$COMMISSION_RESPONSE"

echo ""
echo "✅ Integration test complete!"
echo ""
echo "📊 Expected Results:"
echo "   - Premium partner should get 15% commission (1.5x bonus) on click ($2.00 base)"
echo "   - Expected commission: $2.00 * 0.10 * 1.5 = $0.30"
echo "   - Engagement should get 15% commission on $5.00 base = $0.75"
