# API Endpoints - Sistema de Ventas Online

## Base URL

```
http://localhost:8000/api/v1
```

## Autenticación

Todos los endpoints protegidos requieren un JWT en el header:

```
Authorization: Bearer {access_token}
```

---

## 1. AUTH ENDPOINTS

### POST /auth/register
Registro de nuevo usuario (cliente).

**Request:**
```json
{
  "email": "cliente@example.com",
  "password": "Password123",
  "full_name": "Juan Pérez",
  "phone": "987654321"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "cliente@example.com",
    "full_name": "Juan Pérez",
    "role": "USER"
  }
}
```

**Errors:**
- `400`: Email ya registrado
- `422`: Validación de campos

---

### POST /auth/login
Login con email/password.

**Request:**
```json
{
  "email": "cliente@example.com",
  "password": "Password123"
}
```

**Response (200):**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "cliente@example.com",
    "full_name": "Juan Pérez",
    "role": "USER"
  }
}
```

**Errors:**
- `401`: Credenciales inválidas
- `403`: Usuario inactivo

---

### POST /auth/google-auth  
Login/registro con Google OAuth.

**Request:**
```json
{
  "credential": "google_jwt_token_here"
}
```

**Response (200):**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "email": "usuario@gmail.com",
    "full_name": "María García",
    "role": "USER",
    "auth_provider": "GOOGLE"
  }
}
```

---

### POST /auth/refresh-token
Refrescar access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "new_access_token...",
  "token_type": "bearer"
}
```

**Errors:**
- `401`: Refresh token inválido o expirado

---

### GET /auth/me 🔒
Obtener información del usuario autenticado.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "cliente@example.com",
  "full_name": "Juan Pérez",
  "phone": "987654321",
  "role": "USER",
  "created_at": "2024-01-08T10:00:00Z"
}
```

---

## 2. PUBLIC ENDPOINTS

### GET /public/categories
Listar categorías activas.

**Query Params:**
- `page` (int, default=1)
- `limit` (int, default=20)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Electrónica",
      "slug": "electronica",
      "description": "Productos electrónicos y tecnología"
    }
  ],
  "total": 4,
  "page": 1,
  "pages": 1
}
```

---

### GET /public/categories/{slug}/products
Productos de una categoría.

**Path Params:**
- `slug`: Slug de la categoría

**Query Params:**
- `page` (int, default=1)
- `limit` (int, default=20)

**Response (200):**
```json
{
  "category": {
    "id": 1,
    "name": "Electrónica",
    "slug": "electronica"
  },
  "items": [
    {
      "id": 1,
      "name": "Laptop HP 15\"",
      "slug": "laptop-hp-15",
      "description": "Laptop HP con procesador Intel i5...",
      "price": 2500.00,
      "stock": 10,
      "image_url": "/uploads/products/laptop-hp.jpg",
      "category": {
        "id": 1,
        "name": "Electrónica",
        "slug": "electronica"
      }
    }
  ],
  "total": 3,
  "page": 1,
  "pages": 1
}
```

---

### GET /public/products
Listar todos los productos activos.

**Query Params:**
- `page` (int, default=1)
- `limit` (int, default=20)
- `category_id` (int, optional)
- `min_price` (float, optional)
- `max_price` (float, optional)

**Response:** Similar a `/categories/{slug}/products`

---

### GET /public/products/{id}
Detalle de un producto.

**Response (200):**
```json
{
  "id": 1,
  "name": "Laptop HP 15\"",
  "slug": "laptop-hp-15",
  "description": "Laptop HP con procesador Intel i5, 8GB RAM, 256GB SSD",
  "price": 2500.00,
  "stock": 10,
  "category": {
    "id": 1,
    "name": "Electrónica",
    "slug": "electronica"
  },
  "images": [
    {
      "id": 1,
      "image_url": "/uploads/products/laptop-hp.jpg",
      "thumbnail_url": "/uploads/products/thumbnails/laptop-hp.jpg",
      "is_primary": true
    }
  ],
  "created_at": "2024-01-08T10:00:00Z"
}
```

**Errors:**
- `404`: Producto no encontrado

---

### GET /public/search
Buscar productos.

**Query Params:**
- `q` (string, required): Término de búsqueda
- `page` (int, default=1)
- `limit` (int, default=20)

**Response (200):**
```json
{
  "query": "laptop",
  "items": [
    {
      "id": 1,
      "name": "Laptop HP 15\"",
      "price": 2500.00,
      "image_url": "...",
      ...
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```

---

## 3. CART ENDPOINTS 🔒

### GET /cart
Obtener carrito del usuario autenticado.

**Response (200):**
```json
{
  "id": 1,
  "items": [
    {
      "id": 10,
      "product": {
        "id": 1,
        "name": "Laptop HP 15\"",
        "price": 2500.00,
        "stock": 10,
        "image_url": "..."
      },
      "quantity": 2,
      "subtotal": 5000.00
    }
  ],
  "subtotal": 5000.00,
  "total": 5000.00
}
```

---

### POST /cart/items
Agregar producto al carrito.

**Request:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response (201):**
```json
{
  "id": 10,
  "product_id": 1,
  "quantity": 2,
  "subtotal": 5000.00
}
```

**Errors:**
- `400`: Stock insuficiente
- `404`: Producto no encontrado

---

### PUT /cart/items/{id}
Actualizar cantidad de item.

**Request:**
```json
{
  "quantity": 3
}
```

**Response (200):**
```json
{
  "id": 10,
  "product_id": 1,
  "quantity": 3,
  "subtotal": 7500.00
}
```

---

### DELETE /cart/items/{id}
Eliminar item del carrito.

**Response (204):** No content

---

## 4. CHECKOUT ENDPOINTS 🔒

### POST /checkout/validate
Validar carrito antes de checkout (stock disponible).

**Response (200):**
```json
{
  "valid": true,
  "items": [
    {
      "product_id": 1,
      "available_stock": 10,
      "requested_quantity": 2,
      "valid": true
    }
  ]
}
```

**Response (400) - si hay problemas:**
```json
{
  "valid": false,
  "errors": [
    {
      "product_id": 1,
      "product_name": "Laptop HP",
      "available_stock": 1,
      "requested_quantity": 2,
      "message": "Stock insuficiente"
    }
  ]
}
```

---

### POST /checkout/create-order-yape
Crear pedido con método Yape.

**Request:**
```json
{
  "shipping_address": {
    "full_name": "Juan Pérez",
    "phone": "987654321",
    "address": "Av. Siempre Viva 123",
    "district": "San Isidro",
    "city": "Lima",
    "reference": "Casa azul, 3er piso"
  }
}
```

**Response (201):**
```json
{
  "order_id": "ORD-20240108-0001",
  "status": "PENDING_PAYMENT",
  "total": 5000.00,
  "payment": {
    "method": "YAPE",
    "qr_url": "/static/yape-qr.png",
    "instructions": "Escanea el QR y envía S/ 5000.00. Incluye el código ORD-20240108-0001 en la descripción del pago."
  },
  "created_at": "2024-01-08T10:00:00Z"
}
```

---

### POST /checkout/create-order-whatsapp
Crear pedido con método WhatsApp.

**Request:** Mismo que Yape

**Response (201):**
```json
{
  "order_id": "ORD-20240108-0002",
  "status": "WAITING_CONTACT",
  "total": 5000.00,
  "payment": {
    "method": "WHATSAPP",
    "whatsapp_link": "https://wa.me/51987654321?text=Hola%2C%20quiero%20comprar%20pedido%20ORD-20240108-0002%0A%0A%F0%9F%93%A6%20Productos%3A%0A-%20Laptop%20HP%20x2%20-%20S%2F%205000.00%0A%0A%F0%9F%92%B0%20Total%3A%20S%2F%205000.00%0A%0A%F0%9F%93%8D%20Direcci%C3%B3n%3A%0AAv.%20Siempre%20Viva%20123%0ASan%20Isidro%2C%20Lima%0AReferencia%3A%20Casa%20azul%0ATel%C3%A9fono%3A%20987654321"
  },
  "created_at": "2024-01-08T10:00:00Z"
}
```

---

## 5. ORDERS ENDPOINTS 🔒

### GET /orders/my-orders
Listar pedidos del usuario autenticado.

**Query Params:**
- `page` (int, default=1)
- `limit` (int, default=20)
- `status` (enum, optional): filtrar por estado

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "order_number": "ORD-20240108-0001",
      "total": 5000.00,
      "status": "PENDING_PAYMENT",
      "payment_method": "YAPE",
      "created_at": "2024-01-08T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```

---

### GET /orders/my-orders/{id}
Detalle de un pedido propio.

**Response (200):**
```json
{
  "id": 1,
  "order_number": "ORD-20240108-0001",
  "status": "PENDING_PAYMENT",
  "shipping": {
    "full_name": "Juan Pérez",
    "phone": "987654321",
    "address": "Av. Siempre Viva 123",
    "district": "San Isidro",
    "city": "Lima",
    "reference": "Casa azul"
  },
  "items": [
    {
      "product_name": "Laptop HP 15\"",
      "product_price": 2500.00,
      "quantity": 2,
      "subtotal": 5000.00
    }
  ],
  "subtotal": 5000.00,
  "total": 5000.00,
  "payment": {
    "method": "YAPE",
    "status": "PENDING"
  },
  "created_at": "2024-01-08T10:00:00Z",
  "updated_at": "2024-01-08T10:00:00Z"
}
```

**Errors:**
- `404`: Pedido no encontrado o no pertenece al usuario

---

## 6. ADMIN - CATEGORIES 🔒👑

### GET /admin/categories
Listar todas las categorías (incluye inactivas).

**Query Params:**
- `page`, `limit`, `search`

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Electrónica",
      "slug": "electronica",
      "description": "...",
      "is_active": true,
      "products_count": 15,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

---

### POST /admin/categories
Crear categoría.

**Request:**
```json
{
  "name": "Electrónica",
  "description": "Productos electrónicos",
  "is_active": true
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Electrónica",
  "slug": "electronica",
  "description": "Productos electrónicos",
  "is_active": true,
  "created_at": "..."
}
```

---

### PUT /admin/categories/{id}
Actualizar categoría.

**Request:** Mismo que POST (campos opcionales)

**Response (200):** Categoría actualizada

---

### DELETE /admin/categories/{id}
Eliminar categoría (soft delete).

**Response (204):** No content

**Errors:**
- `400`: Categoría tiene productos asociados

---

## 7. ADMIN - PRODUCTS 🔒👑

### GET /admin/products
Listar productos (incluye inactivos).

**Query Params:**
- `page`, `limit`, `search`, `category_id`, `is_active`

**Response:** Similar a público pero incluye productos inactivos

---

### POST /admin/products
Crear producto.

**Request:**
```json
{
  "category_id": 1,
  "name": "Laptop HP 15\"",
  "description": "...",
  "price": 2500.00,
  "stock": 10,
  "is_active": true
}
```

**Response (201):** Producto creado

---

### PUT /admin/products/{id}
Actualizar producto.

**Request:** Campos opcionales

**Response (200):** Producto actualizado

---

### DELETE /admin/products/{id}
Eliminar producto (soft delete).

**Response (204):** No content

---

### POST /admin/products/{id}/images
Subir imagen de producto.

**Request:** `multipart/form-data`
- `file`: Archivo de imagen

**Response (201):**
```json
{
  "id": 1,
  "image_url": "/uploads/products/laptop-hp-123456.jpg",
  "thumbnail_url": "/uploads/products/thumbnails/laptop-hp-123456.jpg",
  "is_primary": true
}
```

---

## 8. ADMIN - ORDERS 🔒👑

### GET /admin/orders
Listar todos los pedidos.

**Query Params:**
- `page`, `limit`, `status`, `customer_email`, `date_from`, `date_to`

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "order_number": "ORD-20240108-0001",
      "customer": {
        "id": 2,
        "full_name": "Juan Pérez",
        "email": "cliente@example.com"
      },
      "total": 5000.00,
      "status": "PENDING_PAYMENT",
      "payment_method": "YAPE",
      "created_at": "..."
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

---

### GET /admin/orders/{id}
Detalle completo de pedido.

**Response (200):** Similar a user endpoint pero con más detalles

---

### POST /admin/orders/{id}/confirm-payment
Confirmar pago Yape.

**Request:**
```json
{
  "payment_proof": "Captura de pago adjunta",
  "notes": "Pago confirmado el 08/01/2024"
}
```

**Response (200):**
```json
{
  "order_id": "ORD-20240108-0001",
  "status": "PAID",
  "payment_status": "COMPLETED",
  "stock_updated": true,
  "updated_at": "..."
}
```

**Errors:**
- `400`: Pedido no está en estado PENDING_PAYMENT

---

### POST /admin/orders/{id}/cancel
Cancelar pedido.

**Request:**
```json
{
  "reason": "Cliente solicitó cancelación"
}
```

**Response (200):** Pedido cancelado

---

### POST /admin/orders/{id}/ship
Marcar pedido como enviado.

**Request:**
```json
{
  "tracking_number": "ABC123456",
  "carrier": "Olva Courier"
}
```

**Response (200):** Pedido marcado como SHIPPED

**Errors:**
- `400`: Pedido no está en estado PAID

---

### POST /admin/orders/{id}/deliver
Marcar pedido como entregado.

**Response (200):** Pedido marcado como DELIVERED

**Errors:**
- `400`: Pedido no está en estado SHIPPED

---

## 9. ADMIN - STOCK 🔒👑

### PUT /admin/stock/{product_id}
Ajustar stock manualmente.

**Request:**
```json
{
  "adjustment": 10,
  "reason": "Recepción de nueva mercadería"
}
```

**Response (200):**
```json
{
  "product_id": 1,
  "old_stock": 5,
  "new_stock": 15,
  "adjustment": 10,
  "audit_log_id": 123
}
```

---

## Estados y Códigos HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request (validación) |
| 401 | Unauthorized (no autenticado) |
| 403 | Forbidden (sin permisos) |
| 404 | Not Found |
| 422 | Unprocessable Entity |
| 500 | Internal Server Error |

---

## Notas de Implementación

1. **CORS**: Configurar para permitir frontend
2. **Rate Limiting**: 100 req/min por IP en `/auth/*`
3. **Logging**: Todas las peticiones admin deben loggearse
4. **Validación**: Usar Pydantic models
5. **Docs**: FastAPI genera docs automáticas en `/docs`
