# Sistema de Ventas - Backend FastAPI

Sistema de e-commerce con FastAPI, MySQL y autenticación JWT.

## Setup

1. Crear entorno virtual:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
- Copiar `.env.example` a `.env`
- Ajustar credenciales de MySQL si es necesario

4. Ejecutar servidor:
```bash
python main.py
```

El servidor estará disponible en: http://localhost:8000

## Documentación API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estructura

```
backend/
├── app/
│   ├── models/          # Modelos SQLAlchemy
│   ├── schemas/         # Schemas Pydantic
│   ├── routers/         # Endpoints por módulo
│   ├── services/        # Lógica de negocio
│   └── utils/           # Utilidades
├── uploads/             # Archivos subidos
├── main.py              # Aplicación principal
├── database.py          # Configuración BD
└── requirements.txt     # Dependencias
```

## Credenciales por defecto

- **Admin**: admin@sistema-ventas.com / Admin123
- **Cliente**: cliente@example.com / User123
