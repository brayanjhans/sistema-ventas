# Frontend Structure - Next.js 14

## Estructura de Archivos

```
frontend/
├── app/
│   ├── (public)/                    # Grupo de rutas públicas
│   │   ├── layout.tsx               # Layout público (header/footer)
│   │   ├── page.tsx                 # Home
│   │   ├── categorias/
│   │   │   ├── page.tsx             # Listado categorías
│   │   │   └── [slug]/
│   │   │       └── page.tsx         # Productos por categoría
│   │   ├── productos/
│   │   │   ├── page.tsx             # Todos los productos
│   │   │   ├── buscar/
│   │   │   │   └── page.tsx         # Página de búsqueda
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Detalle producto
│   │   ├── carrito/
│   │   │   └── page.tsx             # Carrito de compras
│   │   ├── checkout/
│   │   │   └── page.tsx             # Checkout (🔒 requiere auth)
│   │   ├── cuenta/
│   │   │   ├── page.tsx             # Perfil (🔒)
│   │   │   └── pedidos/
│   │   │       ├── page.tsx         # Mis pedidos (🔒)
│   │   │       └── [id]/
│   │   │           └── page.tsx     # Detalle pedido (🔒)
│   │   ├── login/
│   │   │   └── page.tsx             # Login cliente
│   │   └── registro/
│   │       └── page.tsx             # Registro cliente
│   │
│   ├── admin/                       # Rutas admin (🔒👑 ADMIN only)
│   │   ├── layout.tsx               # Layout admin (sidebar)
│   │   ├── page.tsx                 # Dashboard admin
│   │   ├── login/
│   │   │   └── page.tsx             # Login admin
│   │   ├── categorias/
│   │   │   ├── page.tsx             # CRUD Categorías
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Editar categoría
│   │   ├── productos/
│   │   │   ├── page.tsx             # CRUD Productos
│   │   │   ├── nuevo/
│   │   │   │   └── page.tsx         # Crear producto
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Editar producto
│   │   ├── pedidos/
│   │   │   ├── page.tsx             # Listado pedidos
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Detalle + acciones
│   │   └── stock/
│   │       └── page.tsx             # Ajuste de stock
│   │
│   ├── api/                         # Route handlers (proxy opcional)
│   │   └── [...all]/
│   │       └── route.ts             # Proxy a FastAPI
│   │
│   ├── layout.tsx                   # Root layout
│   ├── globals.css                  # Estilos globales
│   └── middleware.ts                # Protección de rutas
│
├── components/
│   ├── layout/
│   │   ├── Header.tsx               # Header con nav, logo, cart badge
│   │   ├── Footer.tsx               # Footer sitio
│   │   ├── AdminSidebar.tsx         # Sidebar panel admin
│   │   └── AdminHeader.tsx          # Header admin
│   │
│   ├── product/
│   │   ├── ProductCard.tsx          # Card producto (grid)
│   │   ├── ProductGrid.tsx          # Grid de productos
│   │   ├── ProductDetail.tsx        # Detalle completo
│   │   ├── AddToCartButton.tsx      # Botón agregar al carrito
│   │   └── ProductFilters.tsx       # Filtros de productos
│   │
│   ├── cart/
│   │   ├── CartItem.tsx             # Item en carrito
│   │   ├── CartSummary.tsx          # Resumen total
│   │   ├── CartDrawer.tsx           # Drawer lateral (mini-cart)
│   │   └── CartBadge.tsx            # Badge contador en header
│   │
│   ├── checkout/
│   │   ├── CheckoutStepper.tsx      # Pasos del checkout
│   │   ├── ShippingForm.tsx         # Formulario datos envío
│   │   ├── PaymentMethodSelector.tsx# Selector Yape/WhatsApp
│   │   ├── YapeQRDisplay.tsx        # Mostrar QR + instrucciones
│   │   └── WhatsAppRedirect.tsx     # Componente redirección WA
│   │
│   ├── admin/
│   │   ├── DataTable.tsx            # Tabla reutilizable con paginación
│   │   ├── CategoryForm.tsx         # Form crear/editar categoría
│   │   ├── ProductForm.tsx          # Form crear/editar producto
│   │   ├── ImageUploader.tsx        # Uploader de imágenes
│   │   ├── OrderDetailModal.tsx     # Modal detalle pedido
│   │   ├── OrderActions.tsx         # Botones acciones pedido
│   │   ├── StatsCard.tsx            # Cards estadísticas dashboard
│   │   └── filters/
│   │       ├── OrderFilters.tsx     # Filtros pedidos
│   │       └── ProductFilters.tsx   # Filtros productos
│   │
│   ├── auth/
│   │   ├── LoginForm.tsx            # Login con email/pass
│   │   ├── RegisterForm.tsx         # Registro
│   │   ├── GoogleAuthButton.tsx     # Botón login Google
│   │   └── ProtectedRoute.tsx       # HOC para rutas protegidas
│   │
│   └── ui/                          # Componentes UI base
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Modal.tsx
│       ├── Toast.tsx
│       ├── Spinner.tsx
│       ├── Badge.tsx
│       ├── Dropdown.tsx
│       └── Pagination.tsx
│
├── lib/
│   ├── api.ts                       # Cliente Axios configurado
│   ├── auth.ts                      # Helpers de autenticación
│   ├── utils.ts                     # Utilidades generales
│   └── validators.ts                # Validadores personalizados
│
├── stores/
│   ├── authStore.ts                 # Zustand: autenticación
│   ├── cartStore.ts                 # Zustand: carrito
│   └── uiStore.ts                   # Zustand: UI (modals, toasts)
│
├── types/
│   ├── index.ts                     # TypeScript interfaces
│   ├── api.ts                       # Tipos de API responses
│   └── models.ts                    # Modelos de datos
│
├── hooks/
│   ├── useAuth.ts                   # Hook autenticación
│   ├── useCart.ts                   # Hook carrito
│   ├── useProducts.ts               # Hook productos
│   └── useOrders.ts                 # Hook pedidos
│
├── public/
│   ├── static/
│   │   └── yape-qr.png              # QR fijo de Yape
│   └── uploads/                     # (sym link a backend uploads)
│
├── .env.local                       # Variables de entorno
├── next.config.js                   # Config Next.js
├── tailwind.config.js               # Config Tailwind
├── tsconfig.json                    # Config TypeScript
└── package.json
```

---

## Middleware de Protección de Rutas

**File: `app/middleware.ts`**

```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtVerify } from 'jose'

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value
  const path = request.nextUrl.pathname

  // Rutas admin requieren rol ADMIN
  if (path.startsWith('/admin')) {
    // Excluir página de login
    if (path === '/admin/login') {
      return NextResponse.next()
    }

    if (!token) {
      return NextResponse.redirect(new URL('/admin/login', request.url))
    }

    try {
      const verified = await jwtVerify(
        token,
        new TextEncoder().encode(process.env.JWT_SECRET!)
      )
      
      if (verified.payload.role !== 'ADMIN') {
        return NextResponse.redirect(new URL('/', request.url))
      }
    } catch (error) {
      return NextResponse.redirect(new URL('/admin/login', request.url))
    }
  }

  // Rutas de usuario requieren autenticación
  if (
    path.startsWith('/checkout') ||
    path.startsWith('/cuenta')
  ) {
    if (!token) {
      const redirectUrl = new URL('/login', request.url)
      redirectUrl.searchParams.set('redirect', path)
      return NextResponse.redirect(redirectUrl)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/admin/:path*', '/checkout/:path*', '/cuenta/:path*']
}
```

---

## Stores (Zustand)

### authStore.ts

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  full_name: string
  role: 'USER' | 'ADMIN'
}

interface AuthStore {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setTokens: (access: string, refresh: string) => void
  
  isAuthenticated: boolean
  isAdmin: boolean
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      
      isAuthenticated: false,
      isAdmin: false,
      
      login: async (email, password) => {
        // Implementación llamada al API
      },
      
      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isAdmin: false
        })
        // Limpiar cookies
      },
      
      setTokens: (access, refresh) => {
        set({ accessToken: access, refreshToken: refresh })
      }
    }),
    {
      name: 'auth-storage'
    }
  )
)
```

### cartStore.ts

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface CartItem {
  product_id: number
  name: string
  price: number
  quantity: number
  image_url: string
  stock: number
}

interface CartStore {
  items: CartItem[]
  
  addItem: (product: CartItem) => void
  removeItem: (productId: number) => void
  updateQuantity: (productId: number, quantity: number) => void
  clearCart: () => void
  
  subtotal: number
  total: number
  itemCount: number
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      
      addItem: (product) => {
        const { items } = get()
        const existing = items.find(i => i.product_id === product.product_id)
        
        if (existing) {
          set({
            items: items.map(i =>
              i.product_id === product.product_id
                ? { ...i, quantity: i.quantity + product.quantity }
                : i
            )
          })
        } else {
          set({ items: [...items, product] })
        }
      },
      
      removeItem: (productId) => {
        set({ items: get().items.filter(i => i.product_id !== productId) })
      },
      
      updateQuantity: (productId, quantity) => {
        set({
          items: get().items.map(i =>
            i.product_id === productId ? { ...i, quantity } : i
          )
        })
      },
      
      clearCart: () => set({ items: [] }),
      
      get subtotal() {
        return get().items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
      },
      
      get total() {
        return get().subtotal
      },
      
      get itemCount() {
        return get().items.reduce((sum, item) => sum + item.quantity, 0)
      }
    }),
    {
      name: 'cart-storage'
    }
  )
)
```

---

## Cliente API (Axios)

**File: `lib/api.ts`**

```typescript
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptor para refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = useAuthStore.getState().refreshToken
        const { data } = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/refresh-token`,
          { refresh_token: refreshToken }
        )
        
        useAuthStore.getState().setTokens(data.access_token, refreshToken)
        
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
```

---

## Componentes Clave

### ProductCard.tsx

```typescript
interface ProductCardProps {
  product: {
    id: number
    name: string
    price: number
    image_url: string
    stock: number
  }
}

export function ProductCard({ product }: ProductCardProps) {
  const addToCart = useCartStore(state => state.addItem)
  
  const handleAddToCart = () => {
    addToCart({
      product_id: product.id,
      name: product.name,
      price: product.price,
      quantity: 1,
      image_url: product.image_url,
      stock: product.stock
    })
    // Mostrar toast
  }
  
  return (
    <div className="border rounded-lg p-4 hover:shadow-lg transition">
      <img src={product.image_url} alt={product.name} className="w-full h-48 object-cover" />
      <h3 className="mt-2 font-semibold">{product.name}</h3>
      <p className="text-lg font-bold">S/ {product.price.toFixed(2)}</p>
      <p className="text-sm text-gray-500">Stock: {product.stock}</p>
      <button onClick={handleAddToCart} className="mt-2 w-full bg-blue-600 text-white py-2 rounded">
        Agregar al Carrito
      </button>
    </div>
  )
}
```

### YapeQRDisplay.tsx

```typescript
interface YapeQRDisplayProps {
  orderNumber: string
  total: number
  qrUrl: string
}

export function YapeQRDisplay({ orderNumber, total, qrUrl }: YapeQRDisplayProps) {
  return (
    <div className="max-w-md mx-auto text-center">
      <h2 className="text-2xl font-bold mb-4">¡Pedido Creado!</h2>
      <p className="mb-4">Código de Pedido: <strong>{orderNumber}</strong></p>
      
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <img src={qrUrl} alt="QR Yape" className="mx-auto w-64 h-64" />
      </div>
      
      <div className="mt-6 bg-blue-50 p-4 rounded-lg">
        <h3 className="font-semibold mb-2">Instrucción:</h3>
        <ol className="text-left space-y-2">
          <li>1. Escanea el código QR con tu app Yape</li>
          <li>2. Envía <strong>S/ {total.toFixed(2)}</strong></li>
          <li>3. En la descripción incluye: <strong>{orderNumber}</strong></li>
          <li>4. Confirmaremos tu pago en las próximas horas</li>
        </ol>
      </div>
      
      <button className="mt-6 bg-green-600 text-white px-6 py-3 rounded-lg">
        Ver Mis Pedidos
      </button>
    </div>
  )
}
```

---

## Variables de Entorno

**.env.local:**

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_GOOGLE_CLIENT_ID=tu-google-client-id
JWT_SECRET=tu-secret-key-super-seguro
```

---

## Scripts package.json

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0",
    "react-hook-form": "^7.48.0",
    "jose": "^5.1.0",
    "@tanstack/react-query": "^5.0.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## Notas de Implementación

1. **SSR/CSR**: Usar Server Components donde sea posible, Client Components solo cuando sea necesario (estados, eventos)
2. **Imágenes**: Usar `next/image` para optimización automática
3. **Fonts**: Importar Google Fonts con `next/font`
4. **SEO**: Metadata en cada página con `generateMetadata`
5. **Loading States**: Usar archivos `loading.tsx` en cada ruta
6. **Error Handling**: Archivos `error.tsx` para manejo de errores
7. **Testing**: Jest + React Testing Library para componentes
8. **E2E**: Playwright para flujos completos

---

**Versión**: 1.0  
**Fecha**: 2026-01-08
