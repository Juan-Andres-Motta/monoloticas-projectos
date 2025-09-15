#!/usr/bin/env python3
"""
JWT Token Generator for BFF Testing

This script generates JWT tokens for testing the BFF API endpoints.
The BFF service uses simple JWT parsing without strict validation.
"""

import jwt
import json
from datetime import datetime, timedelta
from typing import Dict, Any


def generate_test_jwt(
    user_id: str = "test_user_123",
    partner_id: str = "partner_fashion_blogger_001",
    email: str = "partner@example.com",
    roles: list = None,
    expires_in_hours: int = 24,
    secret: str = "test_secret_key"
) -> str:
    """
    Generate a test JWT token for BFF authentication

    Args:
        user_id: User identifier
        partner_id: Partner identifier
        email: User email
        roles: List of user roles
        expires_in_hours: Token expiration time in hours
        secret: Secret key for signing (not validated by BFF)

    Returns:
        JWT token string
    """
    if roles is None:
        roles = ["PARTNER"]

    # Token payload
    payload = {
        "userId": user_id,           # Primary claim BFF looks for
        "user_id": user_id,          # Alternative claim
        "sub": user_id,              # Standard JWT subject claim
        "id": user_id,               # Another alternative
        "partnerId": partner_id,
        "email": email,
        "roles": roles,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
        "iss": "alpes-partners-auth",
        "aud": "alpes-partners-bff"
    }

    # Generate token
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def decode_jwt(token: str, secret: str = "test_secret_key") -> Dict[str, Any]:
    """Decode and display JWT token contents"""
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError as e:
        return {"error": f"Invalid token: {str(e)}"}


def main():
    """Generate sample JWT tokens for different test scenarios"""

    print("🔐 JWT Token Generator for BFF Testing")
    print("=" * 50)

    # Test scenarios
    scenarios = [
        {
            "name": "Fashion Blogger Partner",
            "user_id": "user_fashion_001",
            "partner_id": "partner_fashion_blogger_001",
            "email": "fashion.blogger@example.com",
            "roles": ["PARTNER", "INFLUENCER"]
        },
        {
            "name": "Tech Affiliate Partner",
            "user_id": "user_tech_002",
            "partner_id": "partner_tech_affiliate_002",
            "email": "tech.affiliate@example.com",
            "roles": ["PARTNER", "AFFILIATE"]
        },
        {
            "name": "Content Creator",
            "user_id": "user_creator_003",
            "partner_id": "partner_content_creator_003",
            "email": "creator@example.com",
            "roles": ["PARTNER", "CONTENT_CREATOR"]
        }
    ]

    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}")
        print("-" * 30)

        # Generate token
        token = generate_test_jwt(
            user_id=scenario["user_id"],
            partner_id=scenario["partner_id"],
            email=scenario["email"],
            roles=scenario["roles"]
        )

        print(f"Token: {token}")
        print(f"Length: {len(token)} characters")

        # Decode to show contents
        decoded = decode_jwt(token)
        print("Decoded payload:")
        print(json.dumps(decoded, indent=2, default=str))

        print(f"\n🔗 Test with curl:")
        print(f'curl -X POST "http://localhost:8002/api/v1/campaigns/camp_winter_sale/accept" \\')
        print(f'  -H "Authorization: Bearer {token}" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"partner_id": "{scenario["partner_id"]}", "partner_type": "INFLUENCER", "acceptance_terms": {{"commission_type": "CPA", "commission_rate": 10.5, "cookie_duration_days": 30, "promotional_methods": ["social_media"]}}, "estimated_monthly_reach": 50000}}\'')

    print(f"\n🚀 Start the BFF service with:")
    print(f"cd bff && python main.py")
    print(f"\n📖 The BFF extracts userId from the JWT without strict validation.")
    print(f"It looks for: 'userId', 'user_id', 'sub', or 'id' claims.")


if __name__ == "__main__":
    main()