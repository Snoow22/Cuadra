# ADR-008: Sesión con cookie y bloqueo de login en PostgreSQL

- **Estado:** Aceptada
- **Fecha:** 2026-10-12

## Contexto

HU-01 pide que un login correcto entregue una sesión, que uno incorrecto responda 401 sin revelar qué campo falló y que 5 fallos en un minuto bloqueen el login temporalmente. Hay que elegir cómo se autentican las peticiones siguientes y dónde se cuentan los fallos. El cliente es el frontend propio (React + Vite), y no se quieren dependencias nuevas aparte de DRF, que ya estaba previsto en [ADR-007](ADR-007-backend-django.md).

## Decisión

- **Autenticación con la sesión de Django y su cookie**, a través de `SessionAuthentication` de DRF, con CSRF habilitado (`CsrfViewMiddleware`). `DEFAULT_AUTHENTICATION_CLASSES` es una lista: para sumar tokens después basta con agregar su clase, sin tocar las vistas.
- **El login también exige CSRF.** DRF lo omite en las vistas sin sesión; se activa con `csrf_protect` para evitar el *login CSRF* (que alguien inicie tu sesión con su cuenta). El front obtiene la cookie `csrftoken` con `GET /auth/csrf` y la reenvía en la cabecera `X-CSRFToken`.
- **El bloqueo se guarda en una tabla de PostgreSQL**, `intentos_login_fallidos (email, creado_en)`, y se usa sólo a través de `usuarios/bloqueo.py`: `registrar_fallo(email)` y `esta_bloqueado(email)`. El conteo es **por cuenta** (email sin distinguir mayúsculas) en una ventana móvil de 60 s. Desde el 5.º fallo, la API responde **429** sin revisar la contraseña. Los fallos de emails que no existen también cuentan, para que el bloqueo no revele qué cuentas existen.
- La tabla es un registro técnico efímero: cada `registrar_fallo` borra las filas más antiguas que la ventana. [ADR-005](ADR-005-nada-se-borra.md) se refiere a los datos de negocio y no aplica aquí.

## Alternativas descartadas

- **Token de DRF (`authtoken`) o JWT:** sirven para clientes fuera del navegador, pero obligan al front a guardar el token (en `localStorage`, expuesto a XSS) y, en el caso de JWT, exigen una librería y un esquema de revocación. Se puede sumar más adelante sin reemplazar la sesión.
- **Cache de Django en memoria (`LocMemCache`):** cada proceso tiene su propio contador, así que con varios workers el límite efectivo se multiplica, y se pierde al reiniciar.
- **`DatabaseCache`:** comparte el contador, pero exige correr `createcachetable` fuera de las migraciones y no permite consultar el historial de fallos.
- **`django-axes` u otra librería:** resuelve más casos de los necesarios a cambio de una dependencia nueva.
- **Bloqueo por IP:** detrás de un proxy o de una red compartida castiga a usuarios legítimos; además, la historia habla de intentos de login, no de clientes.

## Consecuencias

- El front y la API deben compartir origen: en desarrollo, con el proxy de Vite; en producción, con el mismo dominio. Si no, hay que configurar CORS con credenciales y `CSRF_TRUSTED_ORIGINS`.
- Con `SessionAuthentication` como primera clase, una petición sin sesión a un endpoint protegido recibe **403**, no 401 (DRF sólo responde 401 cuando la clase define `WWW-Authenticate`). El 401 explícito queda reservado para credenciales inválidas en el login.
- Con `DEBUG=False`, las cookies de sesión y CSRF son `Secure`: la demo tiene que servirse por HTTPS.
- Cualquiera puede bloquear una cuenta durante un minuto si conoce su email. La historia lo asume al pedir el bloqueo por intentos.
- `esta_bloqueado` y `registrar_fallo` no son atómicos: una ráfaga de intentos en paralelo puede colar algunos más antes del bloqueo. Si llega a importar, se serializa con un lock por email.
