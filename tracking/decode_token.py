#!/usr/bin/env python3
"""
Decode JWT token to see permissions and tenant
"""
import base64
import json


def decode_jwt_token():
    # Token from .env file
    token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjA0OTc4ODIsImlhdCI6MTc1NzkwNTg4MiwiaXNzIjoiZGF0YXN0YXgiLCJzdWIiOiJjbGllbnQ7YWIzNWNmOGQtMGUwMi00OWU2LWJiYWEtNjEwNGM0ZjU2N2MxO2JXbHpieTB4TFRJd01qVT07MTQ5N2Y4MjhkNSIsInRva2VuaWQiOiIxNDk3ZjgyOGQ1In0.seq5Jy1dbUNNbL1fC8sFDuL-iJH0ravXs729VIp-L9XoAV3DGd0WUtvWWeBROaBYnN_NRhW7G3MRSa4YmDpTeyQPj9yNPpW7707tz9DMC7aqdc0pGwLUfWdkMpVoOL8oVUA-5WF9Fji3R_xaZcI9qITll6Pu-znNUkR5bY38wc6qAU9Bl6emOQHs2XAGT8Vnh5jxvBX_80oxIzjmuAJWjFtSy1HuRIFXBfHChoRSeqeAlTJMvBmVnIwp66prIIoUG5AU4lDpHXZKtJ5immJChjg6_FI1_UJoDcnq5NKuSHMeb7gn7V6aRoFVs9CEir2BmHVZSAuJ8Xmj-oJFH90kKA"

    try:
        # Split the token
        parts = token.split(".")
        if len(parts) != 3:
            print("Invalid JWT token format")
            return

        # Decode header
        header_data = base64.urlsafe_b64decode(parts[0] + "==")
        header = json.loads(header_data.decode("utf-8"))
        print("🔑 Token Header:")
        print(json.dumps(header, indent=2))

        # Decode payload
        payload_data = base64.urlsafe_b64decode(parts[1] + "==")
        payload = json.loads(payload_data.decode("utf-8"))
        print("\n📋 Token Payload:")
        print(json.dumps(payload, indent=2))

        # Extract tenant info
        sub = payload.get("sub", "")
        print(f"\n🏢 Subject: {sub}")

        # Try to extract tenant from subject
        if "client;" in sub:
            parts = sub.split(";")
            print(f"🎯 Possible tenant from subject: {parts}")

    except Exception as e:
        print(f"❌ Error decoding token: {e}")


if __name__ == "__main__":
    decode_jwt_token()
