# Instrucciones para Codex

Este repositorio contiene módulos personalizados para Odoo 19 Community.

## Objetivo

Mantener y revisar los archivos de traducción `es_MX.po` de todos los módulos del repositorio.

El objetivo no es únicamente generar traducciones faltantes, sino asegurar que todas las traducciones existentes sean correctas, naturales, consistentes con Odoo y adecuadas para español de México.

Una traducción existente nunca debe asumirse correcta únicamente porque:

- el `msgstr` no esté vacío;
- no tenga la marca `fuzzy`;
- haya sido generada previamente.

Todas las entradas deben revisarse en contexto.

---

# Identificación de módulos

- Todo directorio que contenga un archivo `__manifest__.py` se considera un módulo de Odoo.
- Los módulos pueden encontrarse en cualquier nivel del repositorio.
- Deben descubrirse de forma recursiva.
- Cada módulo mantiene su propio archivo:

```
<modulo>/i18n/es_MX.po
```

Nunca crear un archivo global de traducciones.

---

# Actualización de traducciones

Para cada módulo:

- Si no existe `i18n`, crearlo.
- Si no existe `es_MX.po`, generarlo.
- Si existe, actualizarlo preservando las traducciones correctas.

Nunca reconstruir completamente un archivo válido si puede actualizarse.

---

# Uso de traducciones existentes

Antes de traducir utilizar como referencia:

1. `i18n/es_MX.po`
2. `i18n/es.po`
3. otros `.po` del módulo
4. traducciones oficiales de Odoo
5. contexto del código
6. traducción nueva generada por Codex

Las traducciones existentes deben conservarse cuando sean correctas.

No deben conservarse si contienen:

- Spanglish;
- traducciones parciales;
- inglés residual;
- errores gramaticales;
- terminología incorrecta;
- traducciones literales poco naturales;
- errores funcionales.

---

# Revisión obligatoria

Cada entrada debe revisarse individualmente.

Para cada `msgid`:

- leer el contexto;
- revisar el `msgstr`;
- consultar Python, XML o manifiesto cuando sea necesario;
- corregir cualquier traducción incorrecta.

No revisar únicamente cadenas vacías o marcadas como `fuzzy`.

---

# Reglas de traducción

Utilizar terminología habitual de Odoo 19.

Priorizar siempre:

- precisión funcional;
- consistencia;
- español natural de México.

Evitar:

- Spanglish;
- traducciones literales;
- anglicismos innecesarios.

No modificar:

- placeholders;
- HTML;
- XML;
- expresiones QWeb;
- variables;
- identificadores técnicos.

Conservar exactamente:

- `%s`
- `%d`
- `%(name)s`
- `{name}`
- `{}`

---

# Terminología preferida

| Inglés | Español |
|---------|----------|
| Sales Order | Orden de venta |
| Purchase Order | Orden de compra |
| Manufacturing Order | Orden de fabricación |
| Delivery Order | Orden de entrega |
| Stock Move | Movimiento de inventario |
| Work Order | Orden de trabajo |
| Project | Proyecto |
| Task | Tarea |
| Timesheet | Hoja de horas |
| Employee | Empleado |
| Customer | Cliente |
| Vendor | Proveedor |
| Warehouse | Almacén |
| Bill of Materials | Lista de materiales |
| Inventory Adjustment | Ajuste de inventario |
| Journal Entry | Asiento contable |
| Payment Terms | Condiciones de pago |
| Pricelist | Lista de precios |
| Asset | Activo |
| Resource | Recurso |
| Rental | Renta |
| Quotation | Cotización |

Cuando el contexto lo requiera, adaptar la traducción (por ejemplo, "Partner" puede significar Contacto, Cliente, Proveedor o Empresa).

---

# Validación

Antes de finalizar:

- ejecutar

```bash
msgfmt --check <modulo>/i18n/es_MX.po
```

- verificar placeholders;
- revisar traducciones parciales;
- revisar posibles palabras en inglés;
- eliminar `fuzzy` únicamente cuando la traducción haya sido validada.

---

# Restricciones

Durante tareas de traducción NO modificar:

- modelos;
- vistas;
- acciones;
- menús;
- lógica de negocio;
- ACL;
- reglas;
- datos;
- XML;
- CSV;
- versiones del módulo.

No crear ni modificar archivos distintos de:

```
i18n/es_MX.po
```

salvo que la tarea lo solicite expresamente.

---

# Reporte final

Al terminar indicar:

- módulos analizados;
- módulos omitidos;
- archivos creados;
- archivos actualizados;
- traducciones modificadas;
- traducciones reutilizadas;
- `fuzzy` eliminados;
- `fuzzy` restantes;
- errores encontrados;
- resultado de `msgfmt --check`.

---

# Principios generales

- Revisar todas las traducciones existentes.
- Preservar únicamente las traducciones correctas.
- Corregir cualquier error detectado.
- Mantener consistencia entre módulos.
- Utilizar terminología de Odoo.
- Evitar Spanglish.
- Evitar traducciones mecánicas.
- Mantener español natural de México.
- No declarar un archivo como revisado si no se inspeccionaron todas sus entradas funcionales.