import sys
import os
sys.path.append(os.getcwd())

import asyncio
from app.database import async_session_maker
from app.models.user import User
from sqlalchemy import select
from app.utils.auth import hash_password, verify_password
from passlib.context import CryptContext

async def check_admin():
    print("Checking admin user...")
    async with async_session_maker() as session:
        try:
            stmt = select(User).where(User.email == "admin@sistema-ventas.com")
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print(f"User FOUND: {user.email}")
                print(f"Role: {user.role}")
                
                # Check password
                is_valid = verify_password("Admin123", user.hashed_password)
                print(f"Credential check: {is_valid}")
                
                if not is_valid:
                    print("Updating password...")
                    user.hashed_password = hash_password("Admin123")
                    await session.commit()
                    print("Password updated to 'Admin123'")
            else:
                print("User NOT found. Creating...")
                new_user = User(
                    email="admin@sistema-ventas.com",
                    hashed_password=hash_password("Admin123"),
                    full_name="Admin User",
                    role="admin",
                    is_active=True
                )
                session.add(new_user)
                await session.commit()
                print("User created!")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_admin())
