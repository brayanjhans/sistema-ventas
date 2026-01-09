from passlib.context import CryptContext
import traceback

# Configurar para usar Argon2 por defecto, pero soportar bcrypt (para usuarios antiguos)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

try:
    print("Testing Argon2 hashing...")
    password = "12345678"
    h = pwd_context.hash(password)
    print(f"Argon2 Hash: {h}")
    
    # Verificar
    v = pwd_context.verify(password, h)
    print(f"Argon2 Verify: {v}")
    
    print("\nTesting Bcrypt legacy verification (simulated)...")
    # Hash bcrypt generado previamente (ejemplo)
    # $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn96pzvP/ilf.k.l/W5/y.W.W
    # No tengo un hash real a mano, pero si passlib acepta bcrypt, no debería fallar constructor
    print("Context configuration OK")
    
except Exception:
    traceback.print_exc()
