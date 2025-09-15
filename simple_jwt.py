#!/usr/bin/env python3
"""
Simple JWT Token Generator without external dependencies
"""

import json
import base64
from datetime import datetime, timedelta


def generate_simple_jwt():
    """Generate a simple JWT token for testing"""

    # Header (not used by BFF validation)
    header = {"typ": "JWT", "alg": "HS256"}

    # Payload with user info
    payload = {
        "userId": "user_fashion_001",
        "user_id": "user_fashion_001",
        "sub": "user_fashion_001",
        "partnerId": "partner_fashion_blogger_001",
        "email": "fashion.blogger@example.com",
        "roles": ["PARTNER", "INFLUENCER"],
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
        "iss": "alpes-partners-auth",
    }

    # Base64 encode header and payload
    header_b64 = (
        base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    )
    payload_b64 = (
        base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    )

    # Simple signature (BFF doesn't validate)
    signature = "fake_signature"

    # Combine parts
    token = f"{header_b64}.{payload_b64}.{signature}"

    return token


if __name__ == "__main__":
    token = generate_simple_jwt()
    print("Generated JWT Token:")
    print(token)
    print("\nToken length:", len(token))

    # Show curl command
    print("\n🔗 Test campaign acceptance with:")
    print(
        f'curl -X POST "http://localhost:8001/api/v1/campaigns/camp_winter_sale/accept" \\'
    )
    print(f'  -H "Authorization: Bearer {token}" \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(
        f'  -d \'{{"partner_id": "partner_fashion_blogger_001", "partner_type": "INFLUENCER", "acceptance_terms": {{"commission_type": "CPA", "commission_rate": 10.5, "cookie_duration_days": 30, "promotional_methods": ["social_media"]}}, "estimated_monthly_reach": 50000}}\''
    )
