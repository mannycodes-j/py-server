"""
Security Module
Authentication, authorization, and security utilities.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Any
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import settings


# ============== PASSWORD HASHING ==============

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ============== API KEY AUTHENTICATION ==============

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> bool:
  
    if not settings.API_KEY:
        return True
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Use secrets.compare_digest to prevent timing attacks
    if not secrets.compare_digest(api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return True


def get_api_key_dependency():
  
    if settings.API_KEY:
        return Depends(verify_api_key)
    return None


# ============== JWT TOKEN AUTHENTICATION ==============

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data."""
    sub: Optional[str] = None
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    jti: Optional[str] = None  # JWT ID for token revocation
    scopes: list[str] = []


http_bearer = HTTPBearer(auto_error=False)


def create_access_token(
    subject: str,
    scopes: list[str] = None,
    expires_delta: Optional[timedelta] = None,
    additional_claims: dict = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject (usually user ID or username)
        scopes: List of permission scopes
        expires_delta: Custom expiration time
        additional_claims: Additional claims to include in token
    
    Returns:
        Encoded JWT token string
    """
    if scopes is None:
        scopes = []
    if additional_claims is None:
        additional_claims = {}
    
    now = datetime.utcnow()
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "jti": secrets.token_urlsafe(16),  # Unique token ID
        "scopes": scopes,
        **additional_claims,
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token."""
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(
        subject=subject,
        expires_delta=expires_delta,
        additional_claims={"type": "refresh"}
    )


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
    
    Returns:
        TokenData containing the decoded payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        token_data = TokenData(
            sub=payload.get("sub"),
            exp=datetime.fromtimestamp(payload.get("exp", 0)),
            iat=datetime.fromtimestamp(payload.get("iat", 0)),
            jti=payload.get("jti"),
            scopes=payload.get("scopes", []),
        )
        
        return token_data
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(http_bearer),
) -> Optional[TokenData]:
    """
    Get current user from JWT token in Authorization header.
    
    Returns None if no token is provided (for optional authentication).
    """
    if not credentials:
        return None
    
    return verify_token(credentials.credentials)


def require_auth(
    credentials: HTTPAuthorizationCredentials = Security(http_bearer),
) -> TokenData:
    """
    Require authentication - raises error if no valid token.
    
    Use this dependency when authentication is mandatory.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return verify_token(credentials.credentials)


def require_scopes(*required_scopes: str):
    """
    Create a dependency that requires specific scopes.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_scopes("admin", "read"))])
    """
    async def scope_checker(
        token_data: TokenData = Depends(require_auth),
    ) -> TokenData:
        for scope in required_scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {scope}",
                )
        return token_data
    
    return scope_checker


# ============== UTILITY FUNCTIONS ==============

def generate_api_key() -> str:
    """Generate a secure random API key."""
    return secrets.token_urlsafe(32)


def generate_secret_key() -> str:
    """Generate a secure random secret key for JWT."""
    return secrets.token_urlsafe(64)
