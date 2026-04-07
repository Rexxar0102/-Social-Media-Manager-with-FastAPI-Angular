# SocialPost Pro

Gestor de redes sociales para programar y publicar automáticamente en Instagram.


## Características

- **Publicaciones de Video** - Sube videos con título, descripción y hashtags
-**Publicaciones de Foto** - Comparte imágenes con caption y hashtags
- **Publicaciones de Texto** - Crea posts de solo texto
- **Calendario** - Visualiza todas tus publicaciones programadas
- **Programación Automática** - Programa publicaciones para que se publiquen automáticamente
- **Dashboard** - Estadísticas de tu actividad en redes sociales

##Tech Stack 

### Frontend
- Angular 17+
- Tailwind CSS
- FullCalendar

### Backend
- FastAPI (Python)
- SQLite
- APScheduler (programación de tareas)

## Requisitos

- Python 3.8+
- Node.js 18+ (para el frontend)

## Instalación

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

La aplicación estará disponible en `http://localhost:4200`

## Configuración de Instagram API

1. Ve a [Facebook Developers](https://developers.facebook.com)
2. Crea una nueva aplicación
3. Agrega "Instagram" como producto
4. Configura el OAuth redirect URI: `http://localhost:8000/auth/callback`
5. Obtén tu Client ID y Client Secret
6. En la app, ve a Configuración e ingresa las credenciales

## Estructura del Proyecto

```
social-post-pro/
├── backend/
│   ├── app/
│   │   ├── main.py          # App FastAPI
│   │   ├── database.py      # Configuración SQLite
│   │   ├── models.py        # Modelos de datos
│   │   ├── routes/          # Endpoints API
│   │   │   ├── posts.py     # CRUD de publicaciones
│   │   │   ├── auth.py      # Autenticación OAuth
│   │   │   └── settings.py  # Configuración
│   │   └── services/
│   │       ├── instagram.py # Integración Instagram API
│   │       └── scheduler.py # Programador de publicaciones
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── pages/
    │   │   │   ├── dashboard/      # Dashboard con estadísticas
    │   │   │   ├── create-post/    # Crear nuevas publicaciones
    │   │   │   ├── posts-list/     # Lista de todas las publicaciones
    │   │   │   ├── calendar/       # Vista de calendario
    │   │   │   └── settings/       # Configuración de cuenta
    │   │   ├── services/
    │   │   │   └── api.service.ts  # Comunicación con backend
    │   │   └── models/
    │   │       └── post.model.ts   # Modelos TypeScript
    │   └── styles.css              # Estilos Tailwind
    └── package.json
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/posts` | Listar todas las publicaciones |
| POST | `/api/posts` | Crear nueva publicación |
| PUT | `/api/posts/{id}` | Actualizar publicación |
| DELETE | `/api/posts/{id}` | Eliminar publicación |
| POST | `/api/posts/{id}/publish` | Publicar ahora |
| GET | `/api/posts/scheduled/calendar` | Eventos del calendario |
| GET | `/api/stats` | Estadísticas |
| GET | `/api/settings` | Estado de conexión |
