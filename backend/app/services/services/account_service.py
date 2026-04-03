from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.account import Account
from app.models.user import User
import structlog

logger = structlog.get_logger(__name__)


# ---- User helpers used by security.py ----

async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


# ---- Account CRUD ----

async def list_accounts(db: AsyncSession, owner_id: str, skip: int = 0, limit: int = 50):
    result = await db.execute(
        select(Account)
        .where(Account.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .order_by(Account.created_at.desc())
    )
    return result.scalars().all()


async def get_account(db: AsyncSession, account_id: str, owner_id: str) -> Optional[Account]:
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def create_account(db: AsyncSession, owner_id: str, data: dict) -> Account:
    account = Account(owner_id=owner_id, **data)
    db.add(account)
    await db.flush()
    await db.refresh(account)
    logger.info("account.created", account_id=account.id, platform=account.platform)
    return account


async def update_account(db: AsyncSession, account: Account, data: dict) -> Account:
    for key, value in data.items():
        setattr(account, key, value)
    await db.flush()
    await db.refresh(account)
    return account


async def delete_account(db: AsyncSession, account: Account):
    await db.delete(account)
    await db.flush()
    logger.info("account.deleted", account_id=account.id)


async def count_accounts(db: AsyncSession, owner_id: str) -> int:
    result = await db.execute(
        select(func.count()).where(Account.owner_id == owner_id)
    )
    return result.scalar_one()