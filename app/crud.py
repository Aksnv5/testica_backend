from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User, RefreshToken
from datetime import datetime
from security import *
async def get_user_by_email(db: AsyncSession, email: str):
    q = await db.execute(select(User).where(User.email == email))
    return q.scalars().first()

async def create_user(db: AsyncSession, name: str, email: str, password: str):
    hashed = hash_password(password)
    user = User(name=name, email=email, hashed_password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_refresh_token(db: AsyncSession, token: str, user_id: int, expires_at: datetime, jti: str):
    rt = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(rt)
    await db.commit()
    await db.refresh(rt)
    return rt

async def revoke_refresh_token(db: AsyncSession, token_value: str):
    q = await db.execute(select(RefreshToken).where(RefreshToken.token == token_value))
    rt = q.scalars().first()
    if not rt:
        return False
    rt.revoked = True
    await db.commit()
    return True

async def get_refresh_token_by_token(db: AsyncSession, token_value: str):
    q = await db.execute(select(RefreshToken).where(RefreshToken.token == token_value))
    return q.scalars().first()
