# Tareas API - Proyecto Final CI/CD Grupo #3 Sistemas Operativos

[![CI - Lint y Tests](https://github.com/anakinSkywalker95/proyecto-final/actions/workflows/ci.yml/badge.svg)](https://github.com/anakinSkywalker95/proyecto-final/actions/workflows/ci.yml)
[![CD - Docker Hub](https://github.com/anakinSkywalker95/proyecto-final/actions/workflows/cd.yml/badge.svg)](https://github.com/anakinSkywalker95/proyecto-final/actions/workflows/cd.yml)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

API REST para gestión de tareas, construida con **Flask + PostgreSQL**, empaquetada con **Docker** y desplegada mediante un pipeline completo de **CI/CD con GitHub Actions**.

---

## Descripcion del Proyecto

Este proyecto demuestra la implementación de un pipeline DevOps completo para una aplicación web universitaria:

- **Backend**: API REST con Flask y SQLAlchemy
- **Base de datos**: PostgreSQL con persistencia en volúmenes Docker
- **Contenedores**: Dockerfile multi-stage optimizado + docker-compose
- **CI**: Lint automático con Pylint y tests con Pytest (cobertura >= 70%)
- **CD**: Build y push automático a Docker Hub al hacer merge a `main`

---

## Arquitectura

```
+----------------------------------------------------------+
|                    DEVELOPER WORKSTATION                 |
|                                                          |
|  git push / pull_request                                 |
+---------------------+------------------------------------+
                      |
                      v
+----------------------------------------------------------+
|                    GITHUB ACTIONS                        |
|                                                          |
|  +-----------------+      +---------------------------+  |
|  |   CI Pipeline   |      |      CD Pipeline          |  |
|  |                 |      |                           |  |
|  | 1. Checkout     |      |  (solo en merge a main)   |  |
|  | 2. Setup Python |      |                           |  |
|  | 3. Cache pip    |      | 1. Checkout               |  |
|  | 4. Pylint lint  |----->| 2. Docker Buildx          |  |
|  | 5. Pytest tests |      | 3. Login Docker Hub       |  |
|  | 6. Coverage XML |      | 4. Build multi-arch image |  |
|  |    (artefacto)  |      | 5. Push latest + sha tags |  |
|  +-----------------+      +-------------+-------------+  |
|                                         |                |
+----------------------------------------------------------+
                                          |
                                          v
+------------------------------------------+
|            DOCKER HUB                    |
|                                          |
|  usuario/tareas-api:latest               |
|  usuario/tareas-api:sha-a1b2c3d          |
|  usuario/tareas-api:1.0.0 (en tags)      |
+------------------------------------------+
                    |
                    | docker pull / docker-compose up
                    v
+----------------------------------------------------------+
|                  ENTORNO DE PRODUCCION                   |
|                                                          |
|  +-------------------+    +---------------------------+  |
|  |  tareas_app       |    |  tareas_postgres          |  |
|  |  (Flask+Gunicorn) |<-->|  (PostgreSQL 16)          |  |
|  |  puerto: 5000     |    |  puerto: 5432             |  |
|  |                   |    |  volumen: postgres_data   |  |
|  +-------------------+    +---------------------------+  |
|           |                         |                    |
|           +-------------------------+                    |
|                    red_tareas (bridge)                   |
+----------------------------------------------------------+
```

---

## Instalacion Local (sin Docker)

### Requisitos
- Python 3.12+
- PostgreSQL 14+ corriendo localmente

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/anakinSkywalker95/proyecto-final.git
cd proyecto-final

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\Scripts\activate        # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus datos de PostgreSQL

# 5. Crear la base de datos en PostgreSQL
psql -U postgres -c "CREATE DATABASE tareas_db;"

# 6. Ejecutar la aplicacion
FLASK_ENV=development python wsgi.py
```

La API estara disponible en `http://localhost:5000`.

---

## Instalacion con Docker

### Requisitos
- Docker 24+
- Docker Compose v2

### Levantar el entorno completo

```bash
# Clonar y entrar al directorio
git clone https://github.com/anakinSkywalker95/proyecto-final.git
cd proyecto-final

# Levantar todos los servicios (app + postgres)
docker compose up --build

# Modo detached (en segundo plano)
docker compose up --build -d

# Ver logs en tiempo real
docker compose logs -f app

# Detener y eliminar contenedores
docker compose down

# Detener y eliminar contenedores + volumen de datos
docker compose down -v
```

La API estara disponible en `http://localhost:5000`.

### Usar la imagen publicada en Docker Hub

```bash
# Sin docker-compose, solo la app (necesita PostgreSQL externo)
docker run -d \
  -p 5000:5000 \
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/tareas_db" \
  anakinSkywalker95/tareas-api:latest
```

---

## Ejecutar Tests

```bash
# Activar entorno virtual primero
source venv/bin/activate

# Ejecutar todos los tests con reporte de cobertura
pytest

# Solo tests sin cobertura (mas rapido)
pytest --no-cov

# Tests con reporte HTML detallado
pytest --cov=app --cov-report=html
# Abrir htmlcov/index.html en el navegador

# Ejecutar un test especifico
pytest tests/test_tasks.py::TestCrearTarea::test_crear_tarea_exitosamente -v
```

---

## Endpoints de la API

Base URL: `http://localhost:5000/api`

### Resumen

| Metodo | Endpoint          | Descripcion                          |
|--------|-------------------|--------------------------------------|
| GET    | /health           | Estado de salud de la app y la BD    |
| GET    | /tareas           | Listar todas las tareas              |
| GET    | /tareas/{id}      | Obtener una tarea por ID             |
| POST   | /tareas           | Crear nueva tarea                    |
| PUT    | /tareas/{id}      | Actualizar una tarea existente       |
| DELETE | /tareas/{id}      | Eliminar una tarea                   |

### Ejemplos con curl

#### Health Check
```bash
curl http://localhost:5000/api/health
# {"base_de_datos": "conectada", "status": "ok"}
```

#### Crear una tarea
```bash
curl -X POST http://localhost:5000/api/tareas \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Estudiar Docker", "descripcion": "Ver tutorial de Compose", "prioridad": "alta"}'
# {
#   "id": 1,
#   "titulo": "Estudiar Docker",
#   "descripcion": "Ver tutorial de Compose",
#   "completada": false,
#   "prioridad": "alta",
#   "creada_en": "2026-03-20T10:00:00",
#   "actualizada_en": "2026-03-20T10:00:00"
# }
```

#### Listar todas las tareas
```bash
curl http://localhost:5000/api/tareas
# {"tareas": [...], "total": 1}
```

#### Filtrar por prioridad
```bash
curl "http://localhost:5000/api/tareas?prioridad=alta"
curl "http://localhost:5000/api/tareas?completada=false"
```

#### Obtener una tarea por ID
```bash
curl http://localhost:5000/api/tareas/1
```

#### Actualizar una tarea
```bash
curl -X PUT http://localhost:5000/api/tareas/1 \
  -H "Content-Type: application/json" \
  -d '{"completada": true, "prioridad": "baja"}'
```

#### Eliminar una tarea
```bash
curl -X DELETE http://localhost:5000/api/tareas/1
# {"mensaje": "Tarea 1 eliminada correctamente"}
```

---

## Estructura del Proyecto

```
proyecto-final/
├── app/
│   ├── __init__.py        # Application Factory (create_app)
│   ├── config.py          # Configuraciones por entorno
│   ├── models.py          # Modelo Tarea con SQLAlchemy
│   └── routes.py          # Endpoints CRUD de la API
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Fixtures de Pytest (app, client, BD)
│   └── test_tasks.py      # 24 tests organizados en 7 clases
├── .github/
│   └── workflows/
│       ├── ci.yml         # Pipeline: Pylint + Pytest + Cobertura
│       └── cd.yml         # Pipeline: Build + Push a Docker Hub
├── Dockerfile             # Multi-stage: builder + production
├── docker-compose.yml     # Orquestacion app + postgres
├── pytest.ini             # Configuracion de Pytest y cobertura
├── .pylintrc              # Reglas de Pylint
├── .env.example           # Plantilla de variables de entorno
├── wsgi.py                # Punto de entrada para Gunicorn
└── requirements.txt       # Dependencias Python
```

---

## Variables de Entorno

| Variable          | Descripcion                        | Default                     |
|-------------------|------------------------------------|------------------------------|
| FLASK_ENV         | Entorno (development/production)   | development                  |
| SECRET_KEY        | Clave secreta de Flask             | dev-secret-key-insegura      |
| DATABASE_URL      | URL completa de PostgreSQL         | postgresql://...localhost/.. |
| POSTGRES_USER     | Usuario de PostgreSQL              | postgres                     |
| POSTGRES_PASSWORD | Contrasena de PostgreSQL           | postgres                     |
| POSTGRES_DB       | Nombre de la base de datos         | tareas_db                    |

---

## Pipeline CI/CD

### CI (Integracion Continua)
Se ejecuta en cada `push` y `pull_request`:

```
Push/PR → Checkout → Setup Python → Cache pip
             ↓
         Pylint (score >= 7.0)
             ↓ (si lint pasa)
         Pytest + Cobertura (>= 70%)
             ↓
         Subir coverage.xml como artefacto
```

### CD (Entrega Continua)
Se ejecuta solo en merge a `main`:

```
Merge a main → Checkout → Docker Buildx
                   ↓
              Login Docker Hub (secrets)
                   ↓
              Build multi-arch (amd64 + arm64)
                   ↓
              Push: latest + sha-XXXXXXX
```

### Secrets requeridos en GitHub
| Secret           | Descripcion                              |
|------------------|------------------------------------------|
| DOCKER_USERNAME  | Tu nombre de usuario en Docker Hub       |
| DOCKER_TOKEN     | Access Token de Docker Hub (no password) |

---

## Autores

| Nombre              | Rol                              |
|---------------------|----------------------------------|
| Josué Erazo         | Desarrollo y DevOps              |
| Diana Chacon        | Apoyo en el desarrollo de la API |
| Jose Nahum Reyes    | Apoyo en docker file             |
| Willian Carbajal    | QA y Automatización de Tests     |
| Grupo #3            | Sistemas Operativos              |

---
