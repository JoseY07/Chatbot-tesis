# Chatbot – Guatemala
Proyecto académico y de referencia para la Procuraduría General de la Nación (PGN).
Implementa un chatbot ciudadano en **Python (FastAPI)** con integración en **WordPress**.

## 🚀 Componentes
- **Backend (FastAPI)**: API con flujos de horarios, sedes y denuncias preliminares.
- **Base de datos**: SQLite (demo), fácil de migrar a PostgreSQL.
- **WordPress Plugin**: shortcode `[pgn_chatbot]` que consume el backend Python.
- **Docker**: despliegue rápido del backend.

## 📂 Estructura
- `/backend`: contiene el código Python
- `/wordpress-plugin`: plugin instalable en WP
- `/docs`: diagramas y documentación

## ▶️ Ejecución local
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Accede a la API en: http://127.0.0.1:8000/docs

## 🧩 WordPress
1. Copia `wordpress-plugin/pgn-chatbot` dentro de `wp-content/plugins/`.
2. Activa el plugin desde el panel de WordPress.
3. Inserta el shortcode en una página:
```
[pgn_chatbot]
```

## 🔐 Producción
- Habilita CORS (variable `ALLOWED_ORIGINS`).
- Migra BD a **PostgreSQL** y configura `DATABASE_URL`.
- HTTPS en proxy (Nginx/Traefik).
- Logging, rate limiting, y anonimización de PII.
