"""
Resource Models
Defines data structures for proxies, cards, emails, and accounts.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
import uuid


class ResourceStatus(str, Enum):
    """Status of a resource."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    DISABLED = "disabled"
    EXPIRED = "expired"
    BANNED = "banned"


class ResourceBase(BaseModel):
    """Base model for all resources."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: ResourceStatus = ResourceStatus.AVAILABLE
    assigned_task_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============== PROXY MODELS ==============

class ProxyType(str, Enum):
    """Types of proxy connections."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter"


class Proxy(ResourceBase):
    """Proxy resource model."""
    host: str
    port: int
    proxy_type: ProxyType = ProxyType.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    latency_ms: Optional[int] = None
    last_checked: Optional[datetime] = None
    success_rate: float = 100.0
    
    @property
    def connection_string(self) -> str:
        """Generate proxy connection string."""
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.proxy_type.value}://{auth}{self.host}:{self.port}"


class ProxyCreate(BaseModel):
    """Schema for creating a proxy."""
    host: str
    port: int
    proxy_type: ProxyType = ProxyType.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None


class ProxyUpdate(BaseModel):
    """Schema for updating a proxy."""
    host: Optional[str] = None
    port: Optional[int] = None
    proxy_type: Optional[ProxyType] = None
    username: Optional[str] = None
    password: Optional[str] = None
    status: Optional[ResourceStatus] = None
    country: Optional[str] = None
    city: Optional[str] = None


# ============== CARD MODELS ==============

class CardType(str, Enum):
    """Types of payment cards."""
    VISA = "visa"
    MASTERCARD = "mastercard"
    AMEX = "amex"
    DISCOVER = "discover"
    OTHER = "other"


class Card(ResourceBase):
    """Payment card resource model."""
    card_type: CardType
    last_four: str
    holder_name: str
    expiry_month: int
    expiry_year: int
    billing_zip: Optional[str] = None
    billing_country: Optional[str] = None
    
    # Sensitive data stored encrypted in production
    number_encrypted: Optional[str] = None
    cvv_encrypted: Optional[str] = None


class CardCreate(BaseModel):
    """Schema for creating a card."""
    card_type: CardType
    number: str
    holder_name: str
    expiry_month: int
    expiry_year: int
    cvv: str
    billing_zip: Optional[str] = None
    billing_country: Optional[str] = None


class CardUpdate(BaseModel):
    """Schema for updating a card."""
    holder_name: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    billing_zip: Optional[str] = None
    billing_country: Optional[str] = None
    status: Optional[ResourceStatus] = None


# ============== EMAIL MODELS ==============

class EmailProvider(str, Enum):
    """Email service providers."""
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    YAHOO = "yahoo"
    ICLOUD = "icloud"
    CUSTOM = "custom"


class Email(ResourceBase):
    """Email account resource model."""
    address: str
    provider: EmailProvider
    password_encrypted: Optional[str] = None
    recovery_email: Optional[str] = None
    phone_linked: Optional[str] = None
    imap_server: Optional[str] = None
    smtp_server: Optional[str] = None
    verified: bool = False
    last_checked: Optional[datetime] = None


class EmailCreate(BaseModel):
    """Schema for creating an email."""
    address: str
    provider: EmailProvider
    password: str
    recovery_email: Optional[str] = None
    phone_linked: Optional[str] = None
    imap_server: Optional[str] = None
    smtp_server: Optional[str] = None


class EmailUpdate(BaseModel):
    """Schema for updating an email."""
    password: Optional[str] = None
    recovery_email: Optional[str] = None
    phone_linked: Optional[str] = None
    status: Optional[ResourceStatus] = None
    verified: Optional[bool] = None


# ============== ACCOUNT MODELS ==============

class AccountPlatform(str, Enum):
    """Platform types for accounts."""
    GENERIC = "generic"
    SOCIAL = "social"
    ECOMMERCE = "ecommerce"
    GAMING = "gaming"
    FINANCIAL = "financial"
    STREAMING = "streaming"


class Account(ResourceBase):
    """Platform account resource model."""
    platform: str
    platform_type: AccountPlatform
    username: str
    email_id: Optional[str] = None  # Reference to Email resource
    password_encrypted: Optional[str] = None
    profile_url: Optional[str] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    cookies: Optional[Dict[str, Any]] = None
    last_login: Optional[datetime] = None
    verified: bool = False


class AccountCreate(BaseModel):
    """Schema for creating an account."""
    platform: str
    platform_type: AccountPlatform
    username: str
    email_id: Optional[str] = None
    password: str
    profile_url: Optional[str] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None


class AccountUpdate(BaseModel):
    """Schema for updating an account."""
    username: Optional[str] = None
    email_id: Optional[str] = None
    password: Optional[str] = None
    profile_url: Optional[str] = None
    two_factor_enabled: Optional[bool] = None
    two_factor_secret: Optional[str] = None
    status: Optional[ResourceStatus] = None
    cookies: Optional[Dict[str, Any]] = None
