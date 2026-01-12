from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import auth, public, admin_categories, admin_products, public_orders, admin_orders, admin_analytics, admin_settings, admin_stock, users, public_receipt
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Sistema de Ventas API",
    description="API para sistema de ventas con autenticación y gestión de productos",
    version="1.0.0",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ensure uploads directory exists
if not os.path.exists(os.path.join(BASE_DIR, "uploads")):
    os.makedirs(os.path.join(BASE_DIR, "uploads"))

app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")

# Include routers
app.include_router(public.router, prefix="/api/v1")  # Public first (no auth)
app.include_router(public_orders.router, prefix="/api/v1")  # Public orders
app.include_router(public_receipt.router, prefix="/api/v1")  # Receipt uploads
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(admin_categories.router, prefix="/api/v1")
app.include_router(admin_products.router, prefix="/api/v1")
app.include_router(admin_orders.router, prefix="/api/v1")  # Admin orders
app.include_router(admin_analytics.router, prefix="/api/v1")  # Admin analytics
app.include_router(admin_settings.router, prefix="/api/v1")  # Admin settings
app.include_router(admin_stock.router, prefix="/api/v1")     # Admin stock

@app.get("/")
def root():
    return {"message": "Sistema de Ventas API v1.0"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
