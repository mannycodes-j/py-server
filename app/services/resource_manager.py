"""
Resource Manager Service
Handles all resource-related operations (proxies, cards, emails, accounts).
"""

from typing import Dict, List, Optional, Type, TypeVar, Generic
from datetime import datetime
from ..models.resources import (
    ResourceBase, ResourceStatus,
    Proxy, ProxyCreate, ProxyUpdate,
    Card, CardCreate, CardUpdate,
    Email, EmailCreate, EmailUpdate,
    Account, AccountCreate, AccountUpdate
)

T = TypeVar('T', bound=ResourceBase)


class BaseResourceStore(Generic[T]):
    """Generic resource store with CRUD operations."""
    
    def __init__(self):
        self._items: Dict[str, T] = {}
    
    def add(self, item: T) -> T:
        """Add a resource."""
        self._items[item.id] = item
        return item
    
    def get(self, item_id: str) -> Optional[T]:
        """Get a resource by ID."""
        return self._items.get(item_id)
    
    def get_all(self, status: Optional[ResourceStatus] = None) -> List[T]:
        """Get all resources, optionally filtered by status."""
        items = list(self._items.values())
        if status:
            items = [i for i in items if i.status == status]
        return items
    
    def update(self, item_id: str, **kwargs) -> Optional[T]:
        """Update a resource."""
        item = self._items.get(item_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        return item
    
    def delete(self, item_id: str) -> bool:
        """Delete a resource."""
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False
    
    def assign_to_task(self, item_id: str, task_id: str) -> Optional[T]:
        """Assign resource to a task."""
        item = self._items.get(item_id)
        if item and item.status == ResourceStatus.AVAILABLE:
            item.assigned_task_id = task_id
            item.status = ResourceStatus.IN_USE
            item.updated_at = datetime.utcnow()
            return item
        return None
    
    def release_from_task(self, item_id: str) -> Optional[T]:
        """Release resource from a task."""
        item = self._items.get(item_id)
        if item and item.status == ResourceStatus.IN_USE:
            item.assigned_task_id = None
            item.status = ResourceStatus.AVAILABLE
            item.updated_at = datetime.utcnow()
            return item
        return None
    
    def get_available(self) -> List[T]:
        """Get all available resources."""
        return [i for i in self._items.values() if i.status == ResourceStatus.AVAILABLE]
    
    def count(self) -> Dict[str, int]:
        """Get count by status."""
        items = list(self._items.values())
        return {
            "total": len(items),
            "available": len([i for i in items if i.status == ResourceStatus.AVAILABLE]),
            "in_use": len([i for i in items if i.status == ResourceStatus.IN_USE]),
            "disabled": len([i for i in items if i.status == ResourceStatus.DISABLED]),
            "expired": len([i for i in items if i.status == ResourceStatus.EXPIRED]),
            "banned": len([i for i in items if i.status == ResourceStatus.BANNED]),
        }


class ResourceManager:
    """
    Singleton service for managing all resources.
    Provides unified access to proxies, cards, emails, and accounts.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.proxies = BaseResourceStore[Proxy]()
        self.cards = BaseResourceStore[Card]()
        self.emails = BaseResourceStore[Email]()
        self.accounts = BaseResourceStore[Account]()
        self._initialized = True
    
    # ============== PROXY OPERATIONS ==============
    
    def create_proxy(self, data: ProxyCreate) -> Proxy:
        """Create a new proxy."""
        proxy = Proxy(
            host=data.host,
            port=data.port,
            proxy_type=data.proxy_type,
            username=data.username,
            password=data.password,
            country=data.country,
            city=data.city
        )
        return self.proxies.add(proxy)
    
    def update_proxy(self, proxy_id: str, data: ProxyUpdate) -> Optional[Proxy]:
        """Update a proxy."""
        return self.proxies.update(proxy_id, **data.dict(exclude_unset=True))
    
    def bulk_create_proxies(self, proxy_list: List[ProxyCreate]) -> List[Proxy]:
        """Create multiple proxies at once."""
        return [self.create_proxy(p) for p in proxy_list]
    
    # ============== CARD OPERATIONS ==============
    
    def create_card(self, data: CardCreate) -> Card:
        """Create a new card."""
        card = Card(
            card_type=data.card_type,
            last_four=data.number[-4:],
            holder_name=data.holder_name,
            expiry_month=data.expiry_month,
            expiry_year=data.expiry_year,
            billing_zip=data.billing_zip,
            billing_country=data.billing_country,
            # In production, encrypt these values
            number_encrypted=data.number,  # Should be encrypted
            cvv_encrypted=data.cvv  # Should be encrypted
        )
        return self.cards.add(card)
    
    def update_card(self, card_id: str, data: CardUpdate) -> Optional[Card]:
        """Update a card."""
        return self.cards.update(card_id, **data.dict(exclude_unset=True))
    
    # ============== EMAIL OPERATIONS ==============
    
    def create_email(self, data: EmailCreate) -> Email:
        """Create a new email."""
        email = Email(
            address=data.address,
            provider=data.provider,
            password_encrypted=data.password,  # Should be encrypted
            recovery_email=data.recovery_email,
            phone_linked=data.phone_linked,
            imap_server=data.imap_server,
            smtp_server=data.smtp_server
        )
        return self.emails.add(email)
    
    def update_email(self, email_id: str, data: EmailUpdate) -> Optional[Email]:
        """Update an email."""
        update_data = data.dict(exclude_unset=True)
        if 'password' in update_data:
            update_data['password_encrypted'] = update_data.pop('password')
        return self.emails.update(email_id, **update_data)
    
    # ============== ACCOUNT OPERATIONS ==============
    
    def create_account(self, data: AccountCreate) -> Account:
        """Create a new account."""
        account = Account(
            platform=data.platform,
            platform_type=data.platform_type,
            username=data.username,
            email_id=data.email_id,
            password_encrypted=data.password,  # Should be encrypted
            profile_url=data.profile_url,
            two_factor_enabled=data.two_factor_enabled,
            two_factor_secret=data.two_factor_secret
        )
        return self.accounts.add(account)
    
    def update_account(self, account_id: str, data: AccountUpdate) -> Optional[Account]:
        """Update an account."""
        update_data = data.dict(exclude_unset=True)
        if 'password' in update_data:
            update_data['password_encrypted'] = update_data.pop('password')
        return self.accounts.update(account_id, **update_data)
    
    # ============== STATISTICS ==============
    
    def get_all_statistics(self) -> Dict:
        """Get statistics for all resource types."""
        return {
            "proxies": self.proxies.count(),
            "cards": self.cards.count(),
            "emails": self.emails.count(),
            "accounts": self.accounts.count()
        }
    
    # ============== TASK RESOURCE MANAGEMENT ==============
    
    def release_task_resources(self, task_id: str):
        """Release all resources assigned to a task."""
        for store in [self.proxies, self.cards, self.emails, self.accounts]:
            for item in store.get_all():
                if item.assigned_task_id == task_id:
                    store.release_from_task(item.id)


# Global instance
resource_manager = ResourceManager()
