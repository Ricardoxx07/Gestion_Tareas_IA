# Gestor de tareas con IA

[![Tests](https://github.com/Ricardoxx07/Gesti-n-de-tareas-IA/actions/workflows/tests.yml/badge.svg)](https://github.com/Ricardoxx07/Gesti-n-de-tareas-IA/actions/workflows/tests.yml)

Backend de gestión de tareas que usa IA para transformar lenguaje natural y el
estado real de las tareas en propuestas estructuradas de planificación. Puede
sugerir tareas, subtareas, prioridades, planes diarios y reprogramaciones, pero
no modifica datos de forma autónoma: las operaciones persistentes requieren
validación del backend y confirmación explícita del usuario.

El proyecto combina una API REST tradicional con una integración LLM local
desacoplada, manteniendo el control de las reglas de negocio y de PostgreSQL en
el backend.

## Problema que resuelve

Un gestor de tareas tradicional almacena pendientes, pero deja al usuario el
trabajo de interpretar actividades escritas informalmente, dividir tareas
grandes, decidir prioridades, detectar días sobrecargados y elegir qué mover de
fecha.

Este proyecto utiliza IA como apoyo para esas decisiones, no como un agente con
control directo sobre los datos. Por ejemplo:

```text
"El viernes debo preparar la presentación y enviar el informe a Ana"
                              |
                              v
propuestas estructuradas de tareas + fechas sugeridas + prioridades
```

Las propuestas se devuelven al cliente para que el usuario las revise. No se
guardan hasta que se envían al endpoint de confirmación correspondiente.

## Flujo principal de IA

```text
Lenguaje natural / tareas existentes
              |
              v
      ProveedorIAInterface
              |
              v
      Respuesta estructurada
              |
              v
      Validación con Pydantic
              |
              v
   Reglas de negocio del backend
              |
              v
   Confirmación del usuario
              |
              v
         PostgreSQL
```

Los endpoints de análisis pueden terminar antes de PostgreSQL porque solo
generan una respuesta. El último tramo del flujo ocurre exclusivamente en los
endpoints de confirmación.

## Highlights técnicos

- **Arquitectura por capas.** FastAPI separa routers HTTP, services con reglas
  de negocio y repositories para persistencia, evitando que los endpoints
  concentren lógica de dominio.
- **Persistencia versionada.** SQLAlchemy trabaja sobre PostgreSQL y Alembic
  mantiene el historial de cambios de esquema, incluidas fechas, prioridades y
  jerarquía de tareas.
- **Autenticación y aislamiento.** JWT identifica al usuario actual y cada
  operación de tareas se limita a sus propios datos.
- **Proveedor LLM desacoplado.** Los servicios dependen de
  `ProveedorIAInterface`, por lo que la misma lógica puede ejecutarse con
  `ProveedorOllama` o con `ProveedorIAFalso` determinista.
- **Salida del LLM como entrada no confiable.** Las respuestas del modelo se
  validan con esquemas Pydantic antes de ingresar a las reglas de negocio.
- **Reglas deterministas antes que inferencias.** El backend interpreta y
  valida fechas, prioridades y referencias permitidas cuando corresponde; el
  modelo no puede inventar identificadores de tareas válidos.
- **Human-in-the-loop.** La IA propone; los endpoints de confirmación son los
  únicos que crean tareas o aplican reprogramaciones.
- **Calidad automatizada.** Hay pruebas unitarias, de API e integración, y
  GitHub Actions ejecuta migraciones y la suite completa en cada cambio.

## Arquitectura

```text
Cliente / Swagger
       |
       v
FastAPI (routers, JWT y validación de entrada)
       |
       v
Services ---------------> ProveedorIAInterface
       |                         |-- ProveedorOllama
       v                         `-- ProveedorIAFalso
Repository
       |
       v
PostgreSQL
```

| Componente | Responsabilidad |
| --- | --- |
| Routers | Exponen la API HTTP, reciben dependencias y devuelven contratos de respuesta. |
| Services | Aplican reglas de negocio, validan contexto y coordinan repositories o proveedores IA. |
| Repositories | Encapsulan el acceso a SQLAlchemy y PostgreSQL. |
| Proveedores IA | Generan propuestas estructuradas sin persistir datos. |

## Características funcionales

- Registro, inicio de sesión y consulta del usuario autenticado.
- CRUD de tareas con fecha límite, prioridad y estado de completado.
- Creación y gestión de subtareas asociadas a una tarea padre.
- Propuestas de tareas desde texto libre con fechas y prioridades sugeridas.
- Descomposición de tareas grandes en subtareas propuestas.
- Recomendación de tareas pendientes y planificación del día.
- Detección de sobrecarga según cantidad de tareas por fecha.
- Propuestas de reprogramación y protección frente a una propuesta
  desactualizada.
- Confirmación selectiva de propuestas antes de crear tareas o modificar fechas.

## Tecnologías

- Python 3.14
- FastAPI y Pydantic
- SQLAlchemy 2 y PostgreSQL
- Alembic
- JWT con `python-jose` y hash de contraseñas con Argon2
- Ollama con `llama3.2:3b` (opcional)
- pytest, httpx y GitHub Actions
- Docker y Docker Compose

## Flujo de uso

1. Registra un usuario mediante `POST /auth/registro`.
2. Inicia sesión en `POST /auth/login` y copia el `access_token`.
3. En Swagger, pulsa **Authorize** e introduce `Bearer <access_token>`.
4. Crea tareas con `POST /tareas` o describe actividades en `POST /ia/planificar`.
5. Revisa las propuestas de IA y confirma solo las que quieras persistir.

```text
POST /ia/planificar
        |
        v
propuestas de tareas (no se guardan)
        |
        v
POST /ia/propuestas/confirmar
        |
        v
tareas creadas en PostgreSQL
```

La reprogramación sigue el mismo principio:

```text
POST /ia/proponer-reprogramacion
        |
        v
propuestas de nuevas fechas (no se aplican)
        |
        v
POST /ia/reprogramaciones/confirmar
        |
        v
fechas actualizadas en PostgreSQL
```

## Endpoints principales

Todos los endpoints de tareas e IA requieren un token JWT, salvo registro e
inicio de sesión.

| Área | Endpoints | Acción |
| --- | --- | --- |
| Autenticación | `POST /auth/registro`, `POST /auth/login`, `GET /auth/me` | Crea cuentas, emite JWT y consulta el usuario actual. |
| Tareas | `GET, POST /tareas`, `GET, PUT, PATCH, DELETE /tareas/{id}` | CRUD de tareas propias. |
| Subtareas | `GET, POST /tareas/{id}/subtareas`, `GET, PUT, PATCH, DELETE /tareas/{id}/subtareas/{subtarea_id}` | Gestiona tareas hijas del padre indicado. |
| Propuestas desde texto | `POST /ia/planificar` | Propone tareas, fechas y prioridades; no persiste nada. |
| Descomposición | `POST /ia/descomponer` | Propone subtareas a partir de una tarea grande; no persiste nada. |
| Recomendación | `POST /ia/recomendar-tareas`, `POST /ia/plan-dia` | Prioriza tareas existentes y arma un plan diario; solo lectura. |
| Carga de trabajo | `POST /ia/detectar-sobrecarga` | Detecta concentración de tareas por día; solo lectura. |
| Reprogramación | `POST /ia/proponer-reprogramacion` | Sugiere movimientos de fecha; no modifica tareas. |
| Confirmaciones | `POST /ia/propuestas/confirmar`, `POST /ia/reprogramaciones/confirmar` | Crea tareas confirmadas o actualiza fechas confirmadas. |

Consulta contratos, ejemplos y códigos de respuesta en la documentación
interactiva de FastAPI: `/docs`.

## Seguridad y reglas de IA

- Las contraseñas se almacenan mediante hash Argon2.
- Cada solicitud protegida obtiene el usuario desde el JWT y solo opera sobre
  sus propios datos.
- Las entradas HTTP y las salidas de IA se validan con Pydantic.
- El contexto que llega al modelo está acotado y ordenado de forma
  determinista; las respuestas también tienen máximos compatibles con los
  flujos de confirmación.
- CORS acepta únicamente los orígenes configurados en `CORS_ORIGINS`; no se
  habilita el comodín `*` junto con credenciales JWT.
- Ollama no se considera una fuente confiable: una respuesta mal estructurada
  se rechaza antes de usarse y devuelve un error controlado.
- Los fallos de proveedor y las respuestas inválidas se registran sin incluir
  prompts, tokens ni contenido crudo generado por el modelo.
- Las reglas deterministas del backend tienen prioridad sobre la sugerencia del
  modelo cuando deben calcularse o validarse fechas, prioridades o relaciones
  con tareas existentes.
- La IA no puede persistir cambios directamente. Solo
  `/ia/propuestas/confirmar` y `/ia/reprogramaciones/confirmar` aplican cambios
  derivados de una propuesta, tras una acción explícita del usuario.

## Instalación local

### Requisitos

- Python 3.14.
- PostgreSQL disponible localmente.
- Git.
- Ollama únicamente si se desea usar el proveedor LLM real.

### Entorno y dependencias

```bash
git clone https://github.com/Ricardoxx07/Gesti-n-de-tareas-IA.git
cd Gesti-n-de-tareas-IA
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

En Windows, activa el entorno con:

```powershell
.venv\Scripts\Activate.ps1
```

### Variables de entorno

Copia la plantilla:

```bash
cp .env.example .env
```

Edita `.env` con las credenciales de tu PostgreSQL local. La plantilla contiene
las variables requeridas por la aplicación:

| Variable | Propósito |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Datos de la instancia PostgreSQL local. |
| `DATABASE_URL` | Cadena de conexión de la API y Alembic. |
| `DATABASE_URL_DOCKER` | Cadena de conexión prevista para el contenedor de API. |
| `TEST_DATABASE_URL` | Base de datos aislada para las pruebas de integración. |
| `JWT_SECRET_KEY` | Clave de firma de los tokens; debe ser larga, aleatoria y privada. |
| `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Configuración de los JWT. |
| `IA_PROVIDER` | `falso` u `ollama`. |
| `OLLAMA_MODEL`, `OLLAMA_URL`, `OLLAMA_TIMEOUT_SECONDS`, `OLLAMA_MAX_TOKENS` | Configuración del proveedor Ollama. |
| `CORS_ORIGINS` | Orígenes de frontend permitidos, separados por comas. |

`.env` y `.env.test` están ignorados por Git. No subas credenciales reales al
repositorio. El backend localiza el único archivo `.env` de la raíz del
repositorio automáticamente.

### Base de datos y migraciones

Crea dos bases de datos vacías en PostgreSQL: una para la aplicación
(`gestor_tareas`, por ejemplo) y otra para pruebas (`gestor_tareas_test`). Sus
URLs deben coincidir con `DATABASE_URL` y `TEST_DATABASE_URL`.

Aplica las migraciones:

```bash
cd backend
alembic upgrade head
```

Para comprobar la versión aplicada:

```bash
cd backend
alembic current
```

### Ejecutar la API

```bash
cd backend
uvicorn api.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000` y Swagger en
`http://127.0.0.1:8000/docs`.

### Usar Ollama localmente

El proyecto funciona sin un LLM real con el proveedor falso:

```env
IA_PROVIDER=falso
```

Ese proveedor sirve para comprobar rutas y flujos, pero devuelve respuestas
deterministas: no interpreta lenguaje natural como un modelo real.

Para usar Ollama y el modelo configurado por defecto:

```bash
ollama pull llama3.2:3b
ollama serve
```

En otra terminal, configura `.env`:

```env
IA_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
OLLAMA_URL=http://localhost:11434
```

Reinicia Uvicorn después de cambiar variables de entorno. Si Ollama está
instalado como servicio, normalmente no será necesario ejecutar `ollama serve`
manualmente.

## Pruebas y CI

Ejecuta toda la suite con la base de pruebas configurada:

```bash
cd backend
python -m pytest -q
```

En cada `push` y `pull request`, GitHub Actions:

1. instala las dependencias;
2. inicia PostgreSQL;
3. aplica las migraciones con Alembic;
4. verifica la sincronización del esquema mediante `alembic check`;
5. ejecuta la suite completa con pytest.

## Docker

El repositorio incluye una ejecución reproducible con Docker Compose para la API
y PostgreSQL. Ejecuta los siguientes comandos desde la raíz del repositorio. Al
iniciar, Compose espera el healthcheck de PostgreSQL, aplica las migraciones de
Alembic y luego inicia Uvicorn.

Con `.env` configurado como se indica arriba, ejecuta:

```bash
docker compose up --build -d
docker compose ps
docker compose logs api --tail=100
curl http://127.0.0.1:8000/
```

Ambos servicios deben aparecer como `healthy`. Para comprobar la revisión de
base de datos desde el contenedor:

```bash
docker compose exec api alembic current
```

Por defecto, Compose usa `IA_PROVIDER=falso` dentro de la API para que el
entorno contenerizado no dependa de una instancia de Ollama fuera de Docker. La
integración real con Ollama sigue disponible mediante la ejecución local.

Para detener los contenedores preservando los datos del volumen PostgreSQL:

```bash
docker compose down
```

No uses `docker compose down -v` salvo que quieras eliminar explícitamente la
base de datos local creada por Docker.

## Estado del proyecto

Este repositorio representa un MVP backend orientado a portafolio. Las siguientes
etapas previstas son consolidar la ejecución reproducible con Docker Compose,
desplegar una demo pública y evaluar una interfaz web como complemento de la
API.
