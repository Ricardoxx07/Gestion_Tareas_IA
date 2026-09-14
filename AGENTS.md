# AGENTS.md

## Proyecto

Este repositorio contiene una aplicación de gestión de tareas con integración de IA.

El objetivo es cerrar un MVP full-stack demostrable para portafolio.

El sistema debe permitir que una persona:

* se registre;
* inicie sesión;
* gestione tareas;
* gestione subtareas;
* obtenga propuestas de planificación mediante IA;
* reciba recomendaciones;
* genere un plan diario;
* detecte sobrecarga;
* reciba propuestas de reprogramación;
* confirme explícitamente cualquier cambio persistente propuesto por IA.

La prioridad actual es completar el frontend, integrar correctamente frontend y backend y cerrar una versión `v1.0.0` desplegable.

---

# Principio fundamental

La regla más importante del proyecto es:

```text
La IA propone.
El usuario confirma.
El backend persiste.
```

La IA nunca debe modificar información persistida por sí sola.

Toda operación derivada de IA que:

* cree tareas;
* cree elementos persistentes;
* cambie fechas;
* reprograme trabajo;

debe requerir una acción explícita del usuario antes de persistirse.

No introducir comportamiento autónomo.

---

# Arquitectura general

La arquitectura objetivo es:

```text
Browser
   |
   v
React + TypeScript
   |
   | REST / JSON / JWT
   v
FastAPI
   |
   v
Services
   |
   +--------------------+
   |                    |
   v                    v
Repositories       ProveedorIAInterface
   |                    |
   v               +----+----+
PostgreSQL         |         |
                Ollama     Falso
```

Frontend y backend son aplicaciones independientes.

Deben poder:

* ejecutarse por separado;
* compilarse por separado;
* probarse por separado;
* desplegarse por separado.

No acoplar el frontend directamente a PostgreSQL ni a implementaciones internas de IA.

El frontend solo debe comunicarse con el backend mediante la API HTTP pública.

---

# Backend

## Estado

El backend está funcional y se considera estable para el alcance actual del MVP.

No debe refactorizarse innecesariamente mientras se construye el frontend.

Antes de modificar cualquier parte del backend por una necesidad del frontend:

1. comprobar que existe una incompatibilidad real;
2. identificar el contrato implicado;
3. explicar el problema;
4. proponer el cambio mínimo;
5. evitar cambios de arquitectura no relacionados.

No modificar contratos únicamente para hacer más cómodo el frontend.

---

# Tecnologías backend

Actualmente se utilizan:

* Python 3.14
* FastAPI
* Pydantic
* SQLAlchemy 2
* PostgreSQL
* Alembic
* JWT
* `python-jose`
* Argon2
* Ollama
* `llama3.2:3b`
* proveedor IA falso
* pytest
* httpx
* GitHub Actions
* Docker
* Docker Compose

---

# Arquitectura backend

El backend sigue una separación por capas:

```text
Routers
   |
   v
Services
   |
   v
Repositories
   |
   v
PostgreSQL
```

Los servicios relacionados con IA consumen:

```text
ProveedorIAInterface
```

con implementaciones:

```text
ProveedorOllama
ProveedorIAFalso
```

Responsabilidades:

## Routers

* exponer HTTP;
* recibir dependencias;
* autenticar cuando corresponda;
* validar entrada mediante esquemas;
* devolver contratos HTTP.

## Services

* implementar reglas de negocio;
* validar contexto;
* coordinar repositories;
* coordinar proveedores IA;
* proteger invariantes.

## Repositories

* encapsular acceso a SQLAlchemy;
* persistir en PostgreSQL;
* limitar consultas según usuario cuando corresponda.

## Proveedores IA

* generar propuestas;
* devolver respuestas estructuradas;
* nunca persistir directamente.

---

# Seguridad backend

El backend ya implementa:

* JWT;
* hash de contraseñas con Argon2;
* aislamiento de información por usuario;
* validación Pydantic;
* CORS configurable;
* tratamiento de respuestas LLM como datos no confiables;
* errores controlados del proveedor IA;
* confirmaciones explícitas para operaciones persistentes provenientes de IA.

La autorización real pertenece al backend.

Nunca asumir que ocultar un botón en frontend constituye seguridad.

No permitir que el frontend decida libremente `user_id` para acceder a datos.

---

# Contratos backend

Antes de crear una integración frontend, inspeccionar SIEMPRE el código real.

Revisar como mínimo:

* router;
* schema Pydantic de request;
* schema Pydantic de response;
* status code;
* comportamiento de errores;
* service relacionado si hay lógica importante.

No inventar campos basándose solamente en nombres de endpoints o documentación resumida.

El código y OpenAPI de FastAPI son la fuente principal para los contratos HTTP.

---

# Endpoints principales

## Autenticación

```text
POST /auth/registro
POST /auth/login
GET /auth/me
```

## Tareas

```text
GET /tareas
POST /tareas

GET /tareas/{id}
PUT /tareas/{id}
PATCH /tareas/{id}
DELETE /tareas/{id}
```

## Subtareas

```text
GET /tareas/{id}/subtareas
POST /tareas/{id}/subtareas

GET /tareas/{id}/subtareas/{subtarea_id}
PUT /tareas/{id}/subtareas/{subtarea_id}
PATCH /tareas/{id}/subtareas/{subtarea_id}
DELETE /tareas/{id}/subtareas/{subtarea_id}
```

## IA

```text
POST /ia/planificar
POST /ia/descomponer
POST /ia/recomendar-tareas
POST /ia/plan-dia
POST /ia/detectar-sobrecarga
POST /ia/proponer-reprogramacion
POST /ia/propuestas/confirmar
POST /ia/reprogramaciones/confirmar
```

No asumir que los endpoints IA comparten estructuras.

Inspeccionar individualmente cada contrato.

---

# IA

La IA puede:

* interpretar texto libre;
* proponer tareas;
* sugerir fechas;
* sugerir prioridades;
* proponer subtareas;
* recomendar tareas;
* generar un plan diario;
* detectar sobrecarga;
* proponer reprogramaciones.

La IA NO puede:

* crear tareas automáticamente;
* modificar fechas automáticamente;
* saltarse validaciones del backend;
* inventar IDs válidos;
* acceder directamente a PostgreSQL;
* ejecutar SQL;
* reemplazar reglas deterministas del backend.

Las reglas deterministas tienen prioridad sobre la sugerencia del modelo.

---

# Proveedores IA

Existen al menos dos proveedores:

```text
ProveedorOllama
ProveedorIAFalso
```

`ProveedorIAFalso` permite probar los flujos sin depender de Ollama.

El frontend no debe depender de cuál proveedor esté activo.

Desde la perspectiva frontend:

```text
Frontend
   |
   v
FastAPI
```

El proveedor IA interno es responsabilidad del backend.

---

# Frontend

## Ubicación

Todo el frontend debe estar contenido en:

```text
/frontend
```

No dispersar archivos React en el backend.

---

# Stack frontend aprobado

Usar:

* React
* TypeScript
* Vite
* React Router
* Axios
* TanStack Query
* React Hook Form
* Zod
* Tailwind CSS
* Lucide React

No agregar sin necesidad:

* Redux
* Zustand
* Next.js
* GraphQL
* SSR
* microfrontends
* Material UI
* Bootstrap
* múltiples frameworks CSS

Si una dependencia nueva parece necesaria, justificarla primero.

---

# Arquitectura frontend

Utilizar aproximadamente:

```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   │   ├── common/
│   │   ├── tareas/
│   │   └── ia/
│   ├── hooks/
│   ├── layouts/
│   ├── pages/
│   ├── routes/
│   ├── schemas/
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
│
├── public/
├── .env.example
├── package.json
├── tsconfig.json
└── vite.config.ts
```

Esta estructura es orientativa.

No crear abstracciones o carpetas vacías únicamente para cumplir el esquema.

---

# Comunicación HTTP frontend

Crear un cliente Axios centralizado.

Utilizar:

```env
VITE_API_URL=http://localhost:8000
```

El resto del proyecto no debe hardcodear la URL del backend.

Ejemplo conceptual:

```text
src/api/client.ts
```

Debe añadir JWT cuando exista sesión.

Evitar duplicar:

```text
Authorization: Bearer ...
```

manualmente en cada llamada.

---

# Autenticación frontend

El backend usa JWT Bearer.

Para este MVP:

* usar `sessionStorage`;
* no usar `localStorage`;
* no hardcodear tokens;
* no imprimir tokens en consola;
* no implementar refresh token si el backend no dispone de ese mecanismo.

Flujo:

```text
login
  |
  v
POST /auth/login
  |
  v
JWT
  |
  v
sessionStorage
  |
  v
GET /auth/me
  |
  v
usuario autenticado
```

Cuando el backend devuelva `401`:

* limpiar sesión;
* invalidar usuario autenticado;
* redirigir a login cuando corresponda;
* evitar bucles de redirección o requests.

---

# Estado frontend

Los datos provenientes del backend deben tratarse principalmente como server state.

Utilizar TanStack Query para:

* usuario;
* tareas;
* subtareas;
* recomendaciones;
* plan diario;
* sobrecarga;
* queries relacionadas con servidor.

Utilizar estado local React para:

* modal abierto;
* selección temporal;
* tabs;
* inputs;
* estados exclusivamente visuales.

No duplicar innecesariamente server state con `useState`.

Después de una mutación persistente, invalidar las queries adecuadas.

---

# Formularios

Usar:

* React Hook Form
* Zod

La validación del frontend existe para mejorar UX.

El backend sigue siendo la fuente de verdad.

No replicar reglas complejas de negocio en React si ya pertenecen al backend.

---

# Manejo de errores

Crear una estrategia consistente.

Interpretar como mínimo:

```text
400 → solicitud inválida
401 → sesión inválida o expirada
403 → operación no permitida
404 → recurso inexistente
409 → conflicto
422 → validación
502 → error comunicándose con proveedor IA
503 → proveedor IA no disponible
network error → API inaccesible
```

Cuando el backend ya devuelva un mensaje seguro y útil, reutilizarlo.

No mostrar al usuario:

* stack traces;
* objetos Axios;
* logs internos;
* respuestas crudas del modelo;
* secretos.

---

# Diseño visual

El frontend debe verse:

* profesional;
* moderno;
* limpio;
* tecnológico;
* orientado a productividad;
* adecuado para portafolio.

No debe parecer:

* una demo escolar;
* un dashboard exageradamente futurista;
* una plantilla genérica sin personalidad;
* una interfaz saturada.

Concepto:

```text
SaaS moderno
+
productividad
+
IA sobria
+
herramientas técnicas
```

---

# Paleta visual

## Fondo

```text
#F8FAFC
slate-50
```

## Superficies

```text
#FFFFFF
```

## Texto principal

```text
#0F172A
slate-900
```

## Texto secundario

```text
#64748B
slate-500
```

## Bordes

```text
#E2E8F0
slate-200
```

## Primario

```text
#4F46E5
indigo-600
```

Hover:

```text
#4338CA
indigo-700
```

Usar en:

* CTA;
* navegación activa;
* enlaces principales;
* acciones primarias.

## IA

```text
#0891B2
cyan-600
```

Utilizar con moderación para:

* análisis IA;
* recomendaciones;
* etiquetas inteligentes;
* iconos relacionados.

No convertir toda la interfaz en morado/cyan solo porque utiliza IA.

## Success

```text
#059669
emerald-600
```

## Warning

```text
#D97706
amber-600
```

## Error

```text
#DC2626
red-600
```

---

# Prioridades

Alta:

```text
red
```

Media:

```text
amber
```

Baja:

```text
emerald o slate
```

Utilizar badges o indicadores discretos.

No colorear tarjetas completas según prioridad salvo razón visual clara.

---

# Tipografía

Preferir:

```text
Inter
```

o stack de sistema equivalente.

Jerarquía aproximada:

```text
Título principal: 28–32px
Título sección: 20–24px
Título componente: 16–18px
Texto: 14–16px
Texto secundario: 12–14px
```

---

# Layout

## Desktop

Sidebar aproximada:

```text
240–260px
```

Navegación:

```text
Dashboard
Tareas
Planificar con IA
Plan del día
Carga de trabajo
```

Zona inferior:

```text
Usuario
Cerrar sesión
```

## Mobile

Sidebar colapsable mediante drawer o navegación equivalente.

Todas las funciones principales deben seguir siendo utilizables.

---

# Pantallas principales

## Login

Debe ser sobrio, limpio y sin ilustraciones innecesarias.

## Registro

Mantener coherencia visual con login.

## Dashboard

Debe mostrar rápidamente:

* tareas pendientes;
* tareas próximas;
* prioridades;
* acceso al plan diario;
* acceso visible a funciones IA.

No crear endpoints backend nuevos únicamente para estadísticas simples que ya pueden derivarse de datos disponibles.

## Tareas

Debe permitir:

* listar;
* crear;
* editar;
* completar;
* eliminar;
* mostrar prioridad;
* mostrar fecha;
* navegar al detalle.

## Detalle de tarea

Mostrar:

* nombre;
* descripción cuando exista;
* prioridad;
* fecha;
* estado;
* subtareas;
* acciones;
* opción de descomposición IA.

## Planificar con IA

Entrada principal de lenguaje natural.

Mostrar propuestas claramente separadas de información persistida.

Debe aparecer algún mensaje equivalente a:

```text
Estas propuestas todavía no han sido guardadas.
```

Confirmar solo después de acción explícita.

## Plan del día

Mostrar:

* orden;
* tarea;
* prioridad;
* motivo.

## Carga de trabajo

Mostrar distribución por fechas o días.

Inicialmente preferir componentes CSS simples antes que agregar una librería gráfica.

## Reprogramación

Mostrar:

```text
tarea
fecha actual → fecha propuesta
motivo
```

Mostrar claramente:

```text
Ningún cambio se aplicará hasta que confirmes.
```

---

# Human-in-the-loop en UI

Nunca esconder la diferencia entre:

```text
PROPUESTA
```

y:

```text
CAMBIO GUARDADO
```

Las acciones de confirmación deben ser visibles y conscientes.

No hacer:

```text
POST /ia/planificar
↓
POST /ia/propuestas/confirmar
```

automáticamente.

Debe existir interacción humana entre ambos pasos.

Lo mismo aplica a reprogramaciones.

---

# CORS

El backend ya utiliza:

```text
CORS_ORIGINS
```

Durante desarrollo se espera algo equivalente a:

```text
http://localhost:5173
```

No sustituirlo por `*` sin razón.

---

# Responsive

Validar como mínimo:

```text
375px
768px
1280px+
```

Prioridad visual: desktop.

Prioridad funcional: todos.

---

# Accesibilidad

Utilizar:

* HTML semántico;
* labels;
* botones reales;
* focus visible;
* navegación por teclado;
* contraste adecuado.

No usar `div` clicables cuando corresponde un botón.

---

# Calidad frontend

Mantener funcionando:

```bash
npm run lint
npm run build
```

No resolver errores TypeScript mediante uso indiscriminado de:

```text
any
as any
@ts-ignore
```

Si realmente son necesarios, justificarlo.

---

# Testing frontend

No construir una suite enorme durante el bootstrap.

Utilizar cuando corresponda:

* Vitest
* React Testing Library

Priorizar pruebas críticas:

* ProtectedRoute;
* autenticación;
* formularios principales;
* propuestas IA;
* confirmaciones;
* componentes con lógica relevante.

---

# Git

Trabajar mediante cambios pequeños y temáticos.

Preferir commits como:

```text
feat(frontend): bootstrap React application
feat(frontend): add authentication flow
feat(frontend): implement task CRUD
feat(frontend): add subtask management
feat(frontend): integrate AI planning
feat(frontend): add daily planning view
feat(frontend): add workload analysis
feat(frontend): implement rescheduling confirmation
test(frontend): cover authentication flow
docs: update full-stack setup
```

No mezclar:

* grandes refactors;
* nueva feature;
* cambios backend;
* estilado completo;

en el mismo commit cuando pueden separarse razonablemente.

---

# Forma de trabajo para Codex

No implementar múltiples fases grandes de una sola vez.

Para cada fase:

1. inspeccionar primero el estado actual del repositorio;
2. leer contratos backend relevantes;
3. describir brevemente el plan;
4. implementar solamente el alcance solicitado;
5. ejecutar checks aplicables;
6. corregir fallos introducidos;
7. resumir archivos modificados;
8. explicar cómo validar manualmente;
9. detenerse.

No continuar automáticamente a la siguiente fase.

El repositorio es la fuente de verdad.

No depender de recordar conversaciones antiguas para conocer el estado actual.

---

# Roadmap frontend

## Fase 0

Inspeccionar backend.

No escribir frontend todavía.

Crear mapa:

```text
pantalla
→ endpoint
→ request
→ response
→ auth requerida
→ errores relevantes
```

## Fase 1

Bootstrap:

* React
* TypeScript
* Vite
* Tailwind
* React Router
* Axios
* TanStack Query
* estructura inicial

## Fase 2

Comunicación frontend → FastAPI.

Validar CORS.

## Fase 3

Autenticación:

* registro;
* login;
* sessionStorage;
* `/auth/me`;
* logout;
* ProtectedRoute;
* 401.

## Fase 4

CRUD de tareas.

## Fase 5

CRUD de subtareas.

## Fase 6

`/ia/planificar` + confirmación.

## Fase 7

Descomposición IA.

## Fase 8

Plan diario.

## Fase 9

Sobrecarga.

## Fase 10

Propuestas y confirmación de reprogramación.

## Fase 11

UX:

* loaders;
* empty states;
* errores;
* toasts;
* responsive;
* accesibilidad.

## Fase 12

Testing, lint, build y limpieza.

## Fase 13

Flujo completo y preparación para despliegue.

---

# Flujo final esperado

Una persona debe poder:

```text
Registro
   ↓
Login
   ↓
Dashboard
   ↓
Crear tarea
   ↓
Crear/ver subtareas
   ↓
Solicitar análisis IA
   ↓
Revisar propuesta
   ↓
Confirmar
   ↓
Ver cambio persistido
   ↓
Planificar día
   ↓
Detectar sobrecarga
   ↓
Solicitar reprogramación
   ↓
Confirmar cambios
   ↓
Logout
```

Todo sin abrir Swagger.

---

# Fuera de alcance antes de v1.0.0

No implementar antes del cierre:

* RAG;
* LangChain;
* agentes autónomos;
* acceso LLM → SQL;
* Redis;
* Kafka;
* colas;
* microservicios;
* WebSockets;
* app móvil;
* múltiples proveedores cloud;
* modelos de pago;
* reprogramación autónoma;
* planificación horaria compleja;
* sistema avanzado de preferencias;
* analytics;
* dark mode complejo;
* animaciones elaboradas.

Si aparece una idea nueva fuera del alcance, documentarla como mejora futura en vez de implementarla.

---

# Prioridad de decisión

Cuando existan varias soluciones razonables, priorizar en este orden:

```text
1. Correctitud
2. Seguridad
3. Compatibilidad con backend existente
4. Simplicidad
5. Mantenibilidad
6. Experiencia de usuario
7. Calidad visual
8. Abstracciones avanzadas
```

No sacrificar los primeros puntos para conseguir código aparentemente más sofisticado.

---

# Documentación existente

Antes de decisiones importantes revisar:

```text
README.md
IA_ROADMAP.md
FRONTEND_ROADMAP.md
```

Estos documentos describen estado, decisiones y alcance.

`AGENTS.md` contiene las reglas operativas permanentes para trabajar en el repositorio.

---

# Definición de terminado

El MVP puede considerarse listo cuando:

* backend sigue estable;
* suite backend pasa;
* frontend compila;
* frontend lint pasa;
* autenticación funciona;
* CRUD funciona;
* subtareas funcionan;
* flujos IA funcionan;
* ninguna propuesta IA se persiste automáticamente;
* errores comunes se entienden;
* interfaz es responsive;
* aplicación puede utilizarse sin Swagger;
* frontend y backend pueden desplegarse independientemente;
* README documenta ejecución completa;
* CI está verde;
* existe una demo pública o una ruta clara y reproducible de despliegue.
