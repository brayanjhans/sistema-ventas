# Scripts de Inicio Rápido

Este archivo contiene comandos útiles para iniciar el sistema rápidamente.

## Iniciar Backend

```powershell
cd C:\laragon\www\sistema-ventas\backend
.\venv\Scripts\activate
python main.py
```

## Iniciar Frontend

```powershell
cd C:\laragon\www\sistema-ventas\frontend
npm run dev
```

## Verificar MySQL

```powershell
C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin\mysql.exe -u root -p123456789 -e "USE sistema-ventas; SELECT COUNT(*) as productos FROM products; SELECT COUNT(*) as categorias FROM categories;"
```

## URLs Importantes

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Admin Panel: http://localhost:3000/admin

## Credenciales

**Admin**:
- Email: admin@sistema-ventas.com
- Password: Admin123

**Cliente de prueba**:
- Email: cliente@example.com
- Password: User123
