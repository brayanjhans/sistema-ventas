from passlib.context import CryptContext
import traceback

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    print("Testing bcrypt...")
    h = pwd_context.hash("12345678")
    print(f"Hash: {h}")
    v = pwd_context.verify("12345678", h)
    print(f"Verify: {v}")
except Exception:
    traceback.print_exc()
