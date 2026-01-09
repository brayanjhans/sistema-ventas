import sys
import os
sys.path.append(os.getcwd())

import asyncio
from app.database import async_session_maker
from app.models.user import User
from sqlalchemy import select
from app.utils.auth import hash_password

async def reset_admin_password():
    print("Iniciando reseteo de password admin...")
    async with async_session_maker() as session:
        try:
            # Buscar admin
            stmt = select(User).where(User.email == "admin@sistema-ventas.com")
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            new_hash = hash_password("Admin123")
            
            if user:
                print(f"Usuario Admin encontrado: {user.email}")
                print("Actualizando password con Argon2...")
                user.password_hash = new_hash # Usar el nombre de campo correcto del modelo
                # Nota: En seed usamos hashed_password? Revisar modelo User
                session.add(user)
                await session.commit()
                print("Password actualizado exitosamente a: Admin123")
            else:
                print("Usuario Admin NO encontrado. Creándolo...")
                # Verificar modelo para nombres correctos de campos
                from app.models.user import UserRole, AuthProvider
                new_user = User(
                    email="admin@sistema-ventas.com",
                    hashed_password=new_hash, 
                    full_name="Admin User",
                    role=UserRole.ADMIN,
                    auth_provider=AuthProvider.EMAIL,
                    is_active=True
                )
                session.add(new_user)
                await session.commit()
                print("Usuario Admin CREADO exitosamente con password: Admin123")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reset_admin_password())
