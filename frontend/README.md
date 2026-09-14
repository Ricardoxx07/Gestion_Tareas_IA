# Frontend — Gestor de tareas con IA

Aplicación React independiente que consume la API FastAPI del proyecto.

## Desarrollo

```bash
npm install
cp .env.example .env
npm run dev
```

Configura `VITE_API_URL` con la URL pública de la API. La configuración local
actual expone la API en `http://localhost:8001`.

## Autenticación

El token JWT se almacena exclusivamente en `sessionStorage`: se elimina al cerrar
la pestaña/sesión del navegador y al cerrar sesión desde la aplicación. El cliente
Axios lo adjunta mediante `Authorization: Bearer <token>` y, ante un `401` en una
solicitud protegida, limpia la sesión y redirige al inicio de sesión.

`sessionStorage` continúa siendo accesible desde JavaScript, por lo que no elimina
el riesgo de XSS. Una evolución apropiada para producción sería una sesión basada
en cookies `HttpOnly`, `Secure` y con protección CSRF, respaldada por cambios
explícitos en el backend.

## Verificación

```bash
npm run lint
npm run build
npm test
```

La suite usa Vitest y React Testing Library. Cubre la protección de rutas, el
ciclo de sesión, los formularios principales, el drawer móvil, las propuestas
de IA y las confirmaciones explícitas antes de persistir o eliminar datos.
