"""
Resource Routes
API endpoints for managing proxies, cards, emails, and accounts.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.resources import (
    ResourceStatus,
    Proxy, ProxyCreate, ProxyUpdate,
    Card, CardCreate, CardUpdate,
    Email, EmailCreate, EmailUpdate,
    Account, AccountCreate, AccountUpdate
)
from ..services.resource_manager import resource_manager

router = APIRouter(prefix="/api/resources", tags=["Resources"])


# ============== PROXY ENDPOINTS ==============

@router.post("/proxies/", response_model=Proxy, status_code=201)
async def create_proxy(data: ProxyCreate):
    """Create a new proxy."""
    return resource_manager.create_proxy(data)


@router.post("/proxies/bulk", response_model=List[Proxy], status_code=201)
async def bulk_create_proxies(data: List[ProxyCreate]):
    """Create multiple proxies at once."""
    return resource_manager.bulk_create_proxies(data)


@router.get("/proxies/", response_model=List[Proxy])
async def get_all_proxies(status: Optional[ResourceStatus] = Query(None)):
    """Get all proxies."""
    return resource_manager.proxies.get_all(status)


@router.get("/proxies/{proxy_id}", response_model=Proxy)
async def get_proxy(proxy_id: str):
    """Get a specific proxy."""
    proxy = resource_manager.proxies.get(proxy_id)
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    return proxy


@router.put("/proxies/{proxy_id}", response_model=Proxy)
async def update_proxy(proxy_id: str, data: ProxyUpdate):
    """Update a proxy."""
    proxy = resource_manager.update_proxy(proxy_id, data)
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    return proxy


@router.delete("/proxies/{proxy_id}")
async def delete_proxy(proxy_id: str):
    """Delete a proxy."""
    if not resource_manager.proxies.delete(proxy_id):
        raise HTTPException(status_code=404, detail="Proxy not found")
    return {"message": "Proxy deleted successfully"}


@router.post("/proxies/{proxy_id}/assign/{task_id}", response_model=Proxy)
async def assign_proxy_to_task(proxy_id: str, task_id: str):
    """Assign a proxy to a task."""
    proxy = resource_manager.proxies.assign_to_task(proxy_id, task_id)
    if not proxy:
        raise HTTPException(
            status_code=400, 
            detail="Proxy not found or not available"
        )
    return proxy


@router.post("/proxies/{proxy_id}/release", response_model=Proxy)
async def release_proxy(proxy_id: str):
    """Release a proxy from its current task."""
    proxy = resource_manager.proxies.release_from_task(proxy_id)
    if not proxy:
        raise HTTPException(
            status_code=400, 
            detail="Proxy not found or not in use"
        )
    return proxy


# ============== CARD ENDPOINTS ==============

@router.post("/cards/", response_model=Card, status_code=201)
async def create_card(data: CardCreate):
    """Create a new card."""
    return resource_manager.create_card(data)


@router.get("/cards/", response_model=List[Card])
async def get_all_cards(status: Optional[ResourceStatus] = Query(None)):
    """Get all cards."""
    return resource_manager.cards.get_all(status)


@router.get("/cards/{card_id}", response_model=Card)
async def get_card(card_id: str):
    """Get a specific card."""
    card = resource_manager.cards.get(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.put("/cards/{card_id}", response_model=Card)
async def update_card(card_id: str, data: CardUpdate):
    """Update a card."""
    card = resource_manager.update_card(card_id, data)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.delete("/cards/{card_id}")
async def delete_card(card_id: str):
    """Delete a card."""
    if not resource_manager.cards.delete(card_id):
        raise HTTPException(status_code=404, detail="Card not found")
    return {"message": "Card deleted successfully"}


@router.post("/cards/{card_id}/assign/{task_id}", response_model=Card)
async def assign_card_to_task(card_id: str, task_id: str):
    """Assign a card to a task."""
    card = resource_manager.cards.assign_to_task(card_id, task_id)
    if not card:
        raise HTTPException(
            status_code=400, 
            detail="Card not found or not available"
        )
    return card


@router.post("/cards/{card_id}/release", response_model=Card)
async def release_card(card_id: str):
    """Release a card from its current task."""
    card = resource_manager.cards.release_from_task(card_id)
    if not card:
        raise HTTPException(
            status_code=400, 
            detail="Card not found or not in use"
        )
    return card


# ============== EMAIL ENDPOINTS ==============

@router.post("/emails/", response_model=Email, status_code=201)
async def create_email(data: EmailCreate):
    """Create a new email."""
    return resource_manager.create_email(data)


@router.get("/emails/", response_model=List[Email])
async def get_all_emails(status: Optional[ResourceStatus] = Query(None)):
    """Get all emails."""
    return resource_manager.emails.get_all(status)


@router.get("/emails/{email_id}", response_model=Email)
async def get_email(email_id: str):
    """Get a specific email."""
    email = resource_manager.emails.get(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.put("/emails/{email_id}", response_model=Email)
async def update_email(email_id: str, data: EmailUpdate):
    """Update an email."""
    email = resource_manager.update_email(email_id, data)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.delete("/emails/{email_id}")
async def delete_email(email_id: str):
    """Delete an email."""
    if not resource_manager.emails.delete(email_id):
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Email deleted successfully"}


@router.post("/emails/{email_id}/assign/{task_id}", response_model=Email)
async def assign_email_to_task(email_id: str, task_id: str):
    """Assign an email to a task."""
    email = resource_manager.emails.assign_to_task(email_id, task_id)
    if not email:
        raise HTTPException(
            status_code=400, 
            detail="Email not found or not available"
        )
    return email


@router.post("/emails/{email_id}/release", response_model=Email)
async def release_email(email_id: str):
    """Release an email from its current task."""
    email = resource_manager.emails.release_from_task(email_id)
    if not email:
        raise HTTPException(
            status_code=400, 
            detail="Email not found or not in use"
        )
    return email


# ============== ACCOUNT ENDPOINTS ==============

@router.post("/accounts/", response_model=Account, status_code=201)
async def create_account(data: AccountCreate):
    """Create a new account."""
    return resource_manager.create_account(data)


@router.get("/accounts/", response_model=List[Account])
async def get_all_accounts(status: Optional[ResourceStatus] = Query(None)):
    """Get all accounts."""
    return resource_manager.accounts.get_all(status)


@router.get("/accounts/{account_id}", response_model=Account)
async def get_account(account_id: str):
    """Get a specific account."""
    account = resource_manager.accounts.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/accounts/{account_id}", response_model=Account)
async def update_account(account_id: str, data: AccountUpdate):
    """Update an account."""
    account = resource_manager.update_account(account_id, data)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.delete("/accounts/{account_id}")
async def delete_account(account_id: str):
    """Delete an account."""
    if not resource_manager.accounts.delete(account_id):
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted successfully"}


@router.post("/accounts/{account_id}/assign/{task_id}", response_model=Account)
async def assign_account_to_task(account_id: str, task_id: str):
    """Assign an account to a task."""
    account = resource_manager.accounts.assign_to_task(account_id, task_id)
    if not account:
        raise HTTPException(
            status_code=400, 
            detail="Account not found or not available"
        )
    return account


@router.post("/accounts/{account_id}/release", response_model=Account)
async def release_account(account_id: str):
    """Release an account from its current task."""
    account = resource_manager.accounts.release_from_task(account_id)
    if not account:
        raise HTTPException(
            status_code=400, 
            detail="Account not found or not in use"
        )
    return account


# ============== STATISTICS ENDPOINT ==============

@router.get("/stats/overview")
async def get_statistics():
    """Get resource statistics overview."""
    return resource_manager.get_all_statistics()
