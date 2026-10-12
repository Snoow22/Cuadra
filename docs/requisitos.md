# Documento de requisitos — Inventario para pequeños negocios

> Versión 1.0 · Estado: aprobado para iniciar desarrollo
> Este documento es la fuente de verdad de lo que se construye en la v1. Si una decisión cambia, se actualiza aquí y se registra en `docs/decisiones/`.

## 1. Contexto y problema

Muchos negocios pequeños llevan su inventario con planillas desconectadas: una para productos, otra para compras, otra para ventas. Relacionar el costo de compra con el precio de venta se hace a mano, y el stock real depende de que nadie se equivoque al copiar datos.

Casos reales que motivan el proyecto:

- Una persona con un pequeño negocio de subastas registra cada artículo con etiquetas, planillas de inventario y hojas de ventas, y luego relaciona manualmente costo y precio: <https://www.reddit.com/r/smallbusiness/comments/1mecoxb/small_business_needs_inventoryinvoicing/>
- Un pequeño fabricante de productos impresos en 3D señala que las planillas dejaron de servirle con más de 50 componentes: <https://www.reddit.com/r/smallbusiness/comments/1qhn7ea/inventory_management_software_for_very_small/>

**Objetivo:** una aplicación que registre productos, compras, ventas y existencias en un solo lugar, con historial confiable y margen por venta calculado automáticamente.

**No es un ERP.** Se resuelve una parte acotada del problema para aprender y poder explicar cada decisión técnica.

## 2. Alcance

### Dentro de la v1

- Crear, editar y desactivar productos.
- Registrar entradas, salidas y ajustes de inventario.
- Consultar existencias actuales.
- Registrar compras y ventas sencillas, con varias líneas.
- Consultar el historial de movimientos.
- Alertas de stock bajo e indicador de quiebres.
- Autenticación de usuarios y protección de los datos.

### Fuera de la v1 (se evaluará después)

- Facturación tributaria y contabilidad.
- Códigos de barras.
- Proveedores avanzados.
- Fabricación y listas de materiales (BOM).
- Multi-negocio (multi-tenant).
- Notificaciones por correo.
- Stock negativo configurable y demanda no atendida.

## 3. Decisiones de diseño

Cada una tiene su registro en `docs/decisiones/`.

| ID | Decisión |
|---|---|
| ADR-001 | Los movimientos son la fuente de verdad. `stock_actual` es un valor en caché que se actualiza en la misma transacción que crea el movimiento. |
| ADR-002 | No se permite stock negativo. La venta se rechaza con un 409. |
| ADR-003 | Costo promedio ponderado. Cada línea de venta guarda el costo vigente como "foto". |
| ADR-004 | Un solo negocio, con roles `admin` y `operador`. |
| ADR-005 | Nada se borra: los productos se desactivan y los movimientos se corrigen con uno inverso. |
| ADR-006 | Dinero en enteros (CLP), nunca `float`. |

## 4. Glosario

| Término | Significado |
|---|---|
| Movimiento | Registro inmutable de un cambio de stock de un producto. |
| Stock actual | Cantidad disponible. Valor en caché derivado de los movimientos. |
| Stock mínimo | Umbral por producto bajo el cual se muestra una alerta. |
| Quiebre | Período en que un producto tuvo stock 0. |
| Costo promedio | Costo unitario ponderado por las compras, usado para calcular margen. |
| Ajuste | Movimiento manual (merma, conteo físico) con motivo obligatorio. |
| Anulación | Reversión de una compra o venta mediante movimientos inversos. |

## 5. Roles

| Rol | Puede |
|---|---|
| `admin` | Todo: usuarios, productos, movimientos, compras, ventas y anulaciones. |
| `operador` | Registrar movimientos, compras y ventas, y consultar. No gestiona usuarios ni anula documentos. |

## 6. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | `cantidad` siempre es mayor que 0. El signo lo da el tipo de movimiento (`entrada`, `salida`, `ajuste_positivo`, `ajuste_negativo`). |
| RN-02 | Toda compra o venta confirmada genera sus movimientos en una sola transacción. Si algo falla, no queda nada a medias. |
| RN-03 | Una venta no puede dejar `stock_actual` bajo 0. |
| RN-04 | Los ajustes manuales exigen motivo. |
| RN-05 | Compras y ventas confirmadas no se editan. Se anulan, y la anulación genera movimientos inversos. |
| RN-06 | Un producto inactivo no se puede comprar ni vender, pero su historial sigue visible. |
| RN-07 | El `sku` es único. |
| RN-08 | Al registrar una compra: `costo_promedio = (stock × costo_promedio + cantidad × costo_nuevo) / (stock + cantidad)`, redondeado a entero. |
| RN-09 | Un producto está en alerta cuando `stock_actual <= stock_minimo`. |

## 7. Historias de usuario

Criterios en formato Dado / Cuando / Entonces, resumidos. ★ marca las de mayor valor técnico.

### Autenticación

**HU-01 · Iniciar sesión**
- Dado credenciales válidas, cuando inicio sesión, entonces obtengo una sesión.
- Dado credenciales inválidas, entonces recibo 401 sin revelar qué campo falló.
- Dado 5 intentos fallidos en un minuto, entonces el login se bloquea temporalmente.

**HU-02 · Control de roles**
- Dado un `operador`, cuando intento crear usuarios o anular documentos, entonces recibo 403.
- Dado un `operador`, puedo registrar movimientos, compras y ventas.

### Productos

**HU-03 · Crear producto**
- Dado SKU, nombre, unidad, precio y stock mínimo, cuando lo creo, entonces queda con stock 0.
- Dado un SKU repetido, entonces recibo 409.

**HU-04 · Editar producto**
- Puedo cambiar nombre, precio y stock mínimo.
- No puedo editar `stock_actual` directamente; solo mediante movimientos.

**HU-05 · Desactivar producto**
- Dado un producto desactivado, entonces no aparece en las listas de compra y venta.
- Su historial sigue visible y puedo reactivarlo.

**HU-06 · Listar y buscar**
- Busco por nombre o SKU, filtro por activo/inactivo y por "en alerta", con paginación.

### Movimientos

**HU-07 · Ajuste manual**
- Registro una entrada o salida con motivo obligatorio.
- Dado que no indico motivo, entonces recibo 422.

**HU-08 · Historial ★**
- Veo los movimientos de un producto con filtros por fecha y tipo, del más reciente al más antiguo.
- Cada movimiento muestra usuario y documento de origen.

### Compras

**HU-09 · Registrar compra**
- Dadas varias líneas (producto, cantidad, costo), entonces se generan las entradas y se actualizan stock y costo promedio, todo en una transacción.

**HU-10 · Anular compra**
- Dada una compra, cuando la anulo, entonces se generan salidas inversas.
- Dado que anular dejaría el stock negativo (porque ya se vendió parte), entonces se rechaza con un mensaje claro.

### Ventas

**HU-11 · Registrar venta ★**
- Dadas varias líneas, entonces el stock se descuenta de forma atómica.
- Dado que una línea no tiene stock, entonces se revierte toda la venta y el error indica qué producto y cuánto queda.

**HU-12 · Ventas simultáneas ★**
- Dadas 10 ventas en paralelo de 1 unidad sobre un producto con 5, entonces exactamente 5 se aceptan, 5 se rechazan y el stock final es 0.

**HU-13 · Margen por venta**
- Cada venta muestra su margen (precio − costo vigente) por línea y total.

**HU-14 · Anular venta**
- Genera entradas inversas y deja el rastro en el historial.

### Consultas

**HU-15 · Panel de stock**
- Veo existencias actuales, valor del inventario (stock × costo) y productos en alerta.

**HU-16 · Quiebres**
- Veo los productos que estuvieron en 0 y cuántos días en los últimos 30.
- Se calcula reconstruyendo el stock desde los movimientos.

## 8. Requisitos no funcionales

| ID | Requisito |
|---|---|
| RNF-01 | Toda entrada se valida (Zod) y los errores tienen un formato uniforme. |
| RNF-02 | Contraseñas con hash (bcrypt o argon2). Ningún secreto en el repositorio; solo `.env.example`. |
| RNF-03 | Un test de integración por cada regla RN-01 a RN-09, contra PostgreSQL real. |
| RNF-04 | Listados paginados, con respuesta menor a 300 ms con 10.000 productos (se mide y se documenta). |
| RNF-05 | Restricciones en la base de datos (`CHECK`, `UNIQUE`, claves foráneas) que protejan las reglas aunque falle la API. |
| RNF-06 | Demo desplegada con datos de ejemplo y credenciales de prueba. |
| RNF-07 | Todo el sistema levanta localmente con `docker compose up`. |
| RNF-08 | CI en cada push: lint, tipos, tests y build. |

## 9. Modelo de datos (borrador)

```
usuarios        (id, nombre, email, password_hash, rol, activo, creado_en)
productos       (id, sku, nombre, unidad, precio_venta, costo_promedio,
                 stock_actual, stock_minimo, activo, creado_en, actualizado_en)
compras         (id, fecha, usuario_id, nota, anulada)
compra_items    (id, compra_id, producto_id, cantidad, costo_unitario)
ventas          (id, fecha, usuario_id, nota, anulada)
venta_items     (id, venta_id, producto_id, cantidad, precio_unitario, costo_unitario)
movimientos     (id, producto_id, tipo, cantidad, referencia_tipo, referencia_id,
                 usuario_id, motivo, creado_en)
```

Restricciones mínimas:

- `CHECK (stock_actual >= 0)` en `productos`.
- `CHECK (cantidad > 0)` en `compra_items`, `venta_items` y `movimientos`.
- `UNIQUE (sku)` en `productos`.
- `movimientos` sin `UPDATE` ni `DELETE` desde la aplicación.

El diagrama ER y las migraciones definitivas se construyen en la fase 1b.

## 10. Bloqueo atómico de stock

Para evitar que ventas simultáneas dejen el stock negativo, el descuento se hace dentro de una transacción con una condición:

```sql
UPDATE productos
SET stock_actual = stock_actual - $1
WHERE id = $2 AND stock_actual >= $1
RETURNING stock_actual;
```

Si no devuelve fila, no había stock suficiente y se hace rollback de toda la venta. Este caso se verifica con HU-12.

## 11. Plan de entrega

Avance por rebanadas verticales: cada funcionalidad se completa (migración, API, tests e interfaz) antes de pasar a la siguiente, y todo llega a producción desde el inicio.

| Fase | Contenido | Historias |
|---|---|---|
| 0 | Esqueleto andante: repositorio, `docker-compose`, CI, `/health` y despliegue con URL pública. | — |
| 1 | Requisitos, diagrama ER y migraciones. | — |
| 2 | Acceso y primer producto de punta a punta. | HU-01, 02, 03 |
| 3 | Gestión de productos y ajustes. | HU-04 a 07 |
| 4 | Compras y ventas, cerrando con el test de concurrencia. | HU-09, 11, 12 |
| 5 | Consultas y analítica. | HU-08, 13 a 16 |
| 6 | Anulaciones (lo más delicado). | HU-10, 14 |
| 7 | Pulido: errores uniformes, OpenAPI, README, demo. | — |

Si el tiempo aprieta, la v1 puede salir sin HU-10 y HU-14, corrigiendo mediante ajustes.

## 12. Definición de terminado (por historia)

- Migración aplicada y reversible.
- Endpoint con validación y errores uniformes.
- Tests de integración pasando en CI.
- Interfaz conectada a la API.
- Desplegado en la demo.
- Documentación actualizada (OpenAPI y, si corresponde, un ADR).

## 13. Mejoras futuras (v2)

- `permitir_stock_negativo` configurable por negocio.
- Tabla `demanda_no_atendida` para registrar ventas rechazadas por falta de stock.
- Notificaciones por correo para stock bajo.
- Multi-negocio.
- Importación y exportación CSV.
- Códigos de barras.
