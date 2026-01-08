# Arquitectura del Sistema de Ventas Online

## 1. Descripción del Proyecto

### 1.1 Nombres Propuestos

1. **VentasPro** - Sistema profesional de ventas online
2. **ShopFast Peru** - Enfoque en rapidez y mercado peruano
3. **eCommerce Builder** - Plataforma de comercio electrónico modular

### 1.2 Problema que Resuelve

Actualmente, pequeños y medianos negocios en Perú enfrentan dificultades para:
- Vender online de forma profesional sin grandes inversiones
- Integrar métodos de pago locales (Yape) de forma sencilla
- Gestionar inventario y pedidos desde un panel centralizado
- Ofrecer alternativas cuando el cliente no tiene métodos digitales (WhatsApp)

**Objetivo General**: Crear una plataforma completa de e-commerce que permita a negocios locales vender online con métodos de pago adaptados al mercado peruano (Yape + WhatsApp), con un panel administrativo completo y web pública responsive.

### 1.3 Alcance

#### MVP (Versión 1.0)

- ✅ Web pública con catálogo de productos por categorías
- ✅ Carrito de compras funcional
- ✅ Checkout con dos opciones: Yape QR manual y WhatsApp
- ✅ Registro/Login de usuarios (Google + Email/Password)
- ✅ Panel admin (CRUD categorías, productos, gestión de pedidos)
- ✅ Confirmación manual de pagos Yape desde admin
- ✅ Gestión de stock automática
- ✅ Sistema de roles (ADMIN, USER)

#### Roadmap Futuro (Post-MVP)

- 📋 Integración con APIs de pago automatizadas (Niubiz, Culqi)
- 📋 Sistema de cupones de descuento
- 📋 Reportes y analytics avanzados
- 📋 Notificaciones email/SMS automáticas
- 📋 Sistema de reviews y calificaciones
- 📋 Múltiples imágenes por producto
- 📋 Variantes de productos (tallas, colores)
- 📋 Seguimiento de envíos

### 1.4 Actores del Sistema

| Actor | Descripción | Permisos |
|-------|-------------|----------|
| **Visitante** | Usuario anónimo que navega el catálogo | Ver productos, categorías |
| **Usuario Cliente** | Usuario registrado que puede comprar | Carrito, checkout, ver mis pedidos |
| **Admin** | Administrador del sistema | CRUD completo, confirmar pagos, gestionar pedidos |

### 1.5 Flujo General

```
Admin → Publica catálogo → Base de Datos → Refleja en Web Pública
Usuario → Navega y compra → Crea pedido → Notifica Admin
Admin → Confirma pago/Envía → Actualiza estado → Usuario ve cambios
```

**Descripción del Flujo**:
1. Admin crea/edita categorías y productos con precios y stock
2. Web pública refleja inmediatamente los cambios
3. Usuario navega catálogo, agrega productos al carrito
4. Usuario realiza checkout (Yape o WhatsApp)
5. Si Yape: pedido queda PENDING_PAYMENT, admin confirma manualmente
6. Si WhatsApp: pedido queda WAITING_CONTACT, se envía mensaje pre-formateado
7. Admin gestiona el pedido (confirma pago, marca como enviado/entregado)
8. Usuario puede ver el estado de sus pedidos en su cuenta

---

## 2. Stack Técnico y Restricciones

### 2.1 Arquitectura General

```
┌─────────────────────────────────┐
│   Frontend - Next.js 14         │
│  ┌──────────┐  ┌──────────────┐ │
│  │Web Pública│  │ Panel Admin  │ │
│  └──────────┘  └──────────────┘ │
└────────────┬────────────────────┘
             │ HTTP/REST
┌────────────▼────────────────────┐
│    Backend - FastAPI            │
│  ┌──────────┐  ┌──────────────┐ │
│  │ API REST │  │ Auth/RBAC    │ │
│  └──────────┘  └──────────────┘ │
└────────────┬────────────────────┘
             │ SQL
┌────────────▼────────────────────┐
│      MySQL 8.0 Database         │
│    (sistema-ventas)             │
└─────────────────────────────────┘

Servicios Externos:
- Google OAuth
- Yape QR (estático)
- WhatsApp API (wa.me)
```

### 2.2 Stack Detallado

| Capa | Tecnología | Versión | Justificación |
|------|------------|---------|---------------|
| **Frontend** | Next.js | 14.x | SSR/SSG, SEO, App Router, Server Actions |
| **Styling** | Tailwind CSS | 3.x | Desarrollo rápido, diseño moderno |
| **Estado** | Zustand | 4.x | Simple, ligero para carrito y sesión |
| **HTTP Client** | Axios | 1.x | Interceptores para auth, manejo de errores |
| **Forms** | React Hook Form | 7.x | Validación eficiente |
| **Backend** | FastAPI | 0.109+ | Async, documentación auto, validación Pydantic |
| **ORM** | SQLAlchemy | 2.x | ORM robusto con soporte async |
| **Auth** | python-jose + passlib | Latest | JWT + hash de passwords |
| **Database** | MySQL | 8.0 | Requisito establecido |
| **Migraciones** | Alembic | Latest | Control de versiones de BD |

### 2.3 Restricciones Técnicas

#### Base de Datos
- ✅ **MySQL obligatorio** (credenciales: root/123456789)
- ✅ Nombre BD: `sistema-ventas`
- ✅ Character set: `utf8mb4` (soporte emojis)
- ✅ InnoDB para transacciones ACID

#### Autenticación
- ✅ **Usuarios clientes**: Google OAuth + Email/Password
- ✅ **Admin**: Solo Email/Password con rol ADMIN
- ✅ JWT con tiempo de expiración (access token: 60min, refresh: 7 días)

#### Autorización (RBAC)
- ✅ Todas las rutas `/admin/*` requieren rol ADMIN
- ✅ Validación en backend (middleware FastAPI)
- ✅ Si no ADMIN → HTTP 403 Forbidden
- ✅ Validación también en frontend (redirect)

#### Pagos
- ✅ **Yape manual**: QR fijo del negocio
  - Pedido estado: PENDING_PAYMENT
  - Admin confirma manualmente desde panel
  - Descuenta stock al confirmar (transacción)
- ✅ **WhatsApp fallback**: 
  - Pedido estado: WAITING_CONTACT
  - Link `wa.me/51XXXXXXXXX` con mensaje prellenado
  - Cliente contacta directamente

---

## 3. Requisitos Funcionales

### 3.1 Módulo Admin (Solo Rol ADMIN)

#### RF-ADMIN-001: Autenticación Admin
- Login con email/password
- Solo usuarios con rol ADMIN pueden acceder
- Sesión persistente (JWT)
- Logout

#### RF-ADMIN-002: CRUD Categorías
- **Crear**: Nombre, slug (auto-generado), descripción, activo (boolean)
- **Leer**: Listado paginado, búsqueda por nombre
- **Actualizar**: Todos los campos
- **Eliminar**: Soft delete (marca activo=false)

#### RF-ADMIN-003: CRUD Productos
- **Crear**: 
  - Categoría (select)
  - Nombre, descripción
  - Precio (decimal 2 dígitos)
  - Stock (entero positivo)
  - Activo (boolean)
  - Imagen principal (upload)
- **Leer**: Listado paginado, filtros (categoría, activo), búsqueda
- **Actualizar**: Todos los campos
- **Eliminar**: Soft delete

#### RF-ADMIN-004: Gestión de Imágenes
- Upload de imágenes (JPG, PNG, WebP)
- Thumbnail automático (resize)
- Almacenamiento en `/uploads/products/`
- Máximo 2MB por imagen

#### RF-ADMIN-005: Gestión de Pedidos
- **Listado**: 
  - Ver todos los pedidos
  - Filtros: estado, fecha, cliente
  - Orden: más recientes primero
- **Detalle**: 
  - Datos del pedido (ID, fecha, total)
  - Items (productos, cantidades, precios snapshot)
  - Datos del cliente
  - Método de pago
  - Estado actual
- **Acciones**:
  - Confirmar pago Yape (PENDING_PAYMENT → PAID)
  - Cancelar pedido (cualquier estado → CANCELLED)
  - Marcar como enviado (PAID → SHIPPED)
  - Marcar como entregado (SHIPPED → DELIVERED)

#### RF-ADMIN-006: Ajuste Manual de Stock
- Poder ajustar stock producto por producto
- Registro de ajustes (quién, cuándo, cantidad anterior/nueva)

### 3.2 Módulo Web Pública

#### RF-WEB-001: Catálogo de Productos
- **Home**: 
  - Productos destacados
  - Categorías
  - Buscador
- **Categorías**: 
  - Listado de todas las categorías activas
  - Productos por categoría (paginado)
- **Buscar**: 
  - Búsqueda por nombre/descripción
  - Resultados paginados
- **Detalle Producto**:
  - Imagen grande
  - Nombre, descripción, precio
  - Stock disponible
  - Botón "Agregar al carrito"

#### RF-WEB-002: Carrito de Compras
- Agregar producto (validar stock disponible)
- Editar cantidad (validar stock)
- Eliminar item
- Ver subtotal, total
- Persistir carrito (localStorage + BD si autenticado)
- Botón "Proceder al checkout"

#### RF-WEB-003: Autenticación Usuario
- **Registro**:
  - Google OAuth (un click)
  - Email/Password (validar formato, mínimo 8 caracteres)
- **Login**:
  - Google OAuth
  - Email/Password
- **Perfil**:
  - Ver/editar datos personales
  - Cambiar contraseña

#### RF-WEB-004: Checkout
- **Paso 1**: Revisar carrito
- **Paso 2**: Datos de envío
  - Nombre completo
  - Teléfono
  - Dirección completa
  - Distrito/ciudad
  - Referencia
- **Paso 3**: Método de pago
  - Opción A: Yape
  - Opción B: WhatsApp
- **Paso 4**: Confirmación
  - Si Yape: Mostrar QR + instrucciones + código de pedido
  - Si WhatsApp: Redirigir a wa.me con mensaje

#### RF-WEB-005: Mis Pedidos
- Listado de pedidos del usuario
- Ver detalle de cada pedido
- Ver estado actual
- Ver comprobante/resumen

---

## 4. Requisitos No Funcionales

### RNF-001: Seguridad

#### RBAC (Role-Based Access Control)
```python
# Ejemplo de middleware FastAPI
def require_admin(token: str = Depends(oauth2_scheme)):
    user = decode_jwt(token)
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
```

- ✅ Validación de rol en CADA endpoint protegido
- ✅ Middleware FastAPI que verifica JWT y role
- ✅ Frontend verifica rol para mostrar/ocultar rutas

#### Passwords
- ✅ Hash con bcrypt (cost factor 12)
- ✅ Nunca almacenar contraseñas en texto plano
- ✅ Validación: mínimo 8 caracteres, al menos 1 número

#### JWT
- ✅ Access token: 60 minutos
- ✅ Refresh token: 7 días
- ✅ Secret key en variable de entorno
- ✅ Algorithm: HS256

### RNF-002: Validaciones

- ✅ **Stock**: No permitir cantidades negativas
- ✅ **Precios**: Solo números positivos, máximo 2 decimales
- ✅ **Email**: Validar formato RFC 5322
- ✅ **Teléfono**: Formato peruano (9 dígitos)
- ✅ **Imágenes**: Tipos permitidos (JPG, PNG, WebP), máx 2MB

### RNF-003: Consistencia de Stock

```python
# Ejemplo de transacción para descontar stock
async with session.begin():
    # 1. Verificar stock suficiente
    # 2. Actualizar estado pedido
    # 3. Descontar stock
    # Si falla algo → rollback automático
```

- ✅ Stock se descuenta SOLO al confirmar pago (no al crear pedido)
- ✅ Usar transacciones SQL para garantizar atomicidad
- ✅ Validar stock antes de checkout
- ✅ Re-validar stock en backend al crear pedido

### RNF-004: Auditoría

Registrar en tabla `audit_logs`:
- ✅ Quién confirmó un pago (admin_id)
- ✅ Cuándo se cambió estado de pedido
- ✅ Ajustes manuales de stock
- ✅ Cambios importantes en productos/categorías

### RNF-005: Manejo de Errores

**Backend (FastAPI)**:
```json
{
  "detail": "Mensaje de error claro",
  "error_code": "INSUFFICIENT_STOCK",
  "timestamp": "2024-01-08T10:00:00Z"
}
```

**Frontend**:
- ✅ Mostrar mensajes de error amigables
- ✅ Toasts/alertas para feedback visual
- ✅ Loading states durante operaciones

### RNF-006: Performance

- ✅ Paginación: máximo 20 items por página
- ✅ Índices en columnas frecuentes (ver sección BD)
- ✅ Caché de categorías (pocas cambios)
- ✅ Lazy loading de imágenes
- ✅ Optimización de imágenes (WebP, thumbnails)

---

## Continúa en el archivo database_schema.sql y API_ENDPOINTS.md

Este documento es la parte 1 de 3. Los siguientes documentos complementarios son:
- `database_schema.sql` - DDL completo de MySQL con todas las tablas
- `API_ENDPOINTS.md` - Especificación detallada de todos los endpoints
- `FRONTEND_STRUCTURE.md` - Estructura de componentes y rutas de Next.js
- `IMPLEMENTATION_PLAN.md` - Plan de implementación por sprints

**Versión**: 1.0  
**Fecha**: 2026-01-08  
**Autor**: Arquitectura Sistema Ventas
