# Sistema de Ventas Online

Sistema completo de e-commerce con panel admin, carrito de compras y checkout con Yape/WhatsApp.

## 🚀 Stack Tecnológico

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: MySQL 8.0
- **Auth**: JWT + Google OAuth
- **State**: Zustand
- **ORM**: SQLAlchemy (async)

## 📁 Estructura del Proyecto

```
sistema-ventas/
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── schemas/      # Schemas Pydantic
│   │   ├── routers/      # Endpoints
│   │   ├── services/     # Lógica de negocio
│   │   └── utils/        # Utilidades
│   ├── main.py
│   ├── database.py
│   └── requirements.txt
│
├── frontend/             # Next.js 14
│   ├── app/
│   │   ├── (public)/     # Rutas públicas
│   │   └── admin/        # Panel admin
│   ├── components/
│   ├── stores/           # Zustand stores
│   ├── lib/              # Utilidades
│   └── middleware.ts
│
├── database_schema.sql   # DDL MySQL
├── ARQUITECTURA.md       # Documentación técnica
├── API_ENDPOINTS.md      # Spec de API
└── FRONTEND_STRUCTURE.md # Estructura frontend
```

## 🛠️ Setup Inicial

### 1. Base de Datos

```bash
# Ejecutar DDL en MySQL
mysql -u root -p123456789 < database_schema.sql

# Verificar
mysql -u root -p123456789 -e "USE sistema-ventas; SHOW TABLES;"
```

### 2. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
 pip install -r requirements.txt

# Ejecutar servidor
python main.py
```

**API disponible en**: http://localhost:8000  
**Documentación**: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev
```

**App disponible en**: http://localhost:3000

## 🔐 Credenciales por Defecto

### Admin
- Email: `admin@sistema-ventas.com`
- Password: `Admin123`

### Cliente de Prueba
- Email: `cliente@example.com`
- Password: `User123`

## 📊 Base de Datos

**Database**: `sistema-ventas`

### Tablas Principales

- `users` - Usuarios (clientes y admins)
- `categories` - Categorías de productos
- `products` - Productos del catálogo
- `product_images` - Imágenes de productos
- `carts` / `cart_items` - Carritos de compra
- `orders` / `order_items` - Pedidos
- `payments` - Registros de pago
- `audit_logs` - Auditoría
- `refresh_tokens` - Tokens JWT

## 📚 Documentación

- [**ARQUITECTURA.md**](./ARQUITECTURA.md) - Arquitectura completa del sistema
- [**API_ENDPOINTS.md**](./API_ENDPOINTS.md) - Especificación de 40+ endpoints
- [**FRONTEND_STRUCTURE.md**](./FRONTEND_STRUCTURE.md) - Estructura del frontend
- [**Backend README**](./backend/README.md) - Documentación del backend

## 🗓️ Plan de Desarrollo

El proyecto se divide en **12 sprints** (~40 días):

- ✅ **Sprint 0**: Setup inicial (3 días) - **COMPLETADO**
- 📋 **Sprint 1**: Autenticación (5 días)
- 📋 **Sprint 2**: CRUD Categorías (3 días)
- 📋 **Sprint 3**: CRUD Productos (5 días)
- 📋 **Sprint 4**: Catálogo Público (4 días)
- 📋 **Sprint 5**: Carrito (3 días)
- 📋 **Sprint 6**: Checkout Yape (4 días)
- 📋 **Sprint 7**: Checkout WhatsApp (2 días)
- 📋 **Sprint 8**: Gestión Pedidos (4 días)
- 📋 **Sprint 9**: Mis Pedidos (2 días)
- 📋 **Sprint 10**: Ajuste Stock (2días)
- 📋 **Sprint 11**: Testing (3 días)
- 📋 **Sprint 12**: Deploy (2 días)

Ver detalles completos en [ARQUITECTURA.md](./ARQUITECTURA.md#9-plan-de-implementaci%C3%B3n-por-fases)

## 🎯 Características Principales

### Para Clientes
- 🛍️ Catálogo de productos por categorías
- 🛒 Carrito de compras persistente
- 💳 Checkout con Yape QR manual
- 💬 Checkout alternativo por WhatsApp
- 📦 Ver mis pedidos y estados
- 🔐 Login con Google o email/password

### Para Administradores
- 📊 Dashboard con estadísticas
- 🏷️ CRUD completo de categorías
- 📦 CRUD completo de productos
- 🖼️ Upload de imágenes de productos
- 📋 Gestión de pedidos
- ✅ Confirmar pagos Yape manualmente
- 📈 Ajuste manual de stock
- 🔍 Auditoría de cambios

## 🔧 Variables de Entorno

### Backend (.env)
```bash
DATABASE_URL=mysql+aiomysql://root:123456789@localhost:3306/sistema-ventas
JWT_SECRET=tu-secret-key-256-bits
FRONTEND_URL=http://localhost:3000
WHATSAPP_PHONE=51987654321
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_GOOGLE_CLIENT_ID=tu-google-client-id
JWT_SECRET=tu-secret-key-256-bits
```

## 🚦 Estado del Proyecto

### ✅ Completado (Sprint 0)
- Base de datos con 10 tablas
- Backend FastAPI estructurado
- Frontend Next.js 14 configurado
- Stores Zustand (auth, cart)
- Middleware de protección
- Documentación técnica completa

### 🔄 En Desarrollo
- Sistema de autenticación (Sprint 1)

### 📋 Pendiente
- CRUD categorías y productos
- Catálogo público
- Carrito y checkout
- Gestión de pedidos
- Testing y deploy

## 📞 Soporte

Para dudas o problemas, revisar la documentación en:
- [ARQUITECTURA.md](./ARQUITECTURA.md)
- [API_ENDPOINTS.md](./API_ENDPOINTS.md)

---

**Versión**: 1.0.0  
**Última actualización**: 2026-01-08  
**Sprint actual**: 0 de 12 (Setup Inicial) ✅
