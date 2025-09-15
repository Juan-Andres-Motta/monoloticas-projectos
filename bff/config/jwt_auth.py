import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional


security = HTTPBearer()


class JWTAuth:
    """Simple JWT authentication for extracting userId"""

    @staticmethod
    def extract_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """
        Extract userId from JWT token without strict validation.
        This is a simple implementation - in production you'd want proper validation.
        """
        try:
            token = credentials.credentials

            # Decode without verification (not recommended for production)
            # In production, you'd use verify=True with proper secret/public key
            decoded_token = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )

            # Extract userId - try common claim names
            user_id = (
                decoded_token.get("userId") or
                decoded_token.get("user_id") or
                decoded_token.get("sub") or
                decoded_token.get("id")
            )

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="UserId not found in JWT token"
                )

            return str(user_id)

        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid JWT token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error processing JWT token: {str(e)}"
            )

    @staticmethod
    def optional_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
        """
        Extract userId from JWT token if present, return None if not provided
        """
        if not credentials:
            return None

        try:
            return JWTAuth.extract_user_id(credentials)
        except HTTPException:
            return None