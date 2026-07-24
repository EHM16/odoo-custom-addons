# Instrucciones para Codex

Este repositorio contiene módulos personalizados para Odoo 19 Community.

## Objetivo

Mantener y generar archivos de traducción `es_MX.po` para los módulos de este repositorio preservando siempre el trabajo existente y minimizando cambios innecesarios.

---

# Identificación de módulos

- Todo directorio que contenga un archivo `__manifest__.py` se considera un módulo de Odoo.
- Cada módulo debe procesarse de forma completamente independiente.
- Cada módulo debe mantener su propio archivo:

```
<modulo>/i18n/es_MX.po
```

- Nunca crear un archivo de traducciones global para todo el repositorio.

---

# Generación y actualización de traducciones

Para cada módulo:

- Si no existe el directorio `i18n`, crearlo.
- Si no existe `i18n/es_MX.po`, generarlo.
- Si ya existe `i18n/es_MX.po`, actualizarlo sin perder traducciones válidas.
- Incorporar únicamente las cadenas nuevas.
- Eliminar o marcar como obsoletas las cadenas que ya no existan en el código.
- Mantener intactos todos los `msgid`.
- Modificar únicamente los `msgstr`.

Nunca reconstruir completamente un archivo `.po` cuando ya exista uno válido.

---

# Uso de traducciones existentes

Antes de generar o actualizar un archivo `es_MX.po`, utilizar todas las traducciones disponibles como referencia para preservar el trabajo existente.

Seguir el siguiente orden de prioridad:

1. `i18n/es_MX.po` existente.
2. `i18n/es.po`.
3. Cualquier otro archivo `.po` presente en el módulo (`es_419.po`, `fr.po`, `de.po`, `it.po`, etc.).
4. Traducciones oficiales de Odoo.
5. Contexto del código fuente (Python, XML, CSV, reportes, asistentes, manifiesto y demás archivos).
6. Traducción nueva generada por Codex únicamente cuando no exista suficiente contexto.

Objetivos:

- Preservar el trabajo ya realizado.
- Mantener una terminología consistente.
- Evitar reemplazar traducciones correctas por otras equivalentes.
- Completar únicamente las traducciones faltantes.
- Actualizar únicamente las entradas afectadas por cambios en el código.

En caso de conflicto, el código fuente (`msgid`) siempre tiene prioridad.

---

# Herramientas oficiales de Odoo

Siempre que sea posible:

1. Utilizar las herramientas oficiales de internacionalización de Odoo para exportar o actualizar las cadenas traducibles.
2. Fusionar el resultado con el archivo `es_MX.po` existente.
3. Preservar todas las traducciones válidas.
4. Traducir únicamente las nuevas entradas o aquellas cuyo `msgid` haya cambiado.
5. Validar el resultado antes de finalizar.

Evitar editar manualmente un archivo `.po` cuando exista un procedimiento oficial de Odoo que permita mantener correctamente su estructura.

---

# Reglas de traducción

- Analizar siempre el contexto funcional antes de traducir.
- Utilizar la terminología oficial de Odoo siempre que sea adecuada.
- Priorizar la precisión funcional sobre la traducción literal.
- Mantener la misma terminología en todos los módulos del repositorio.
- No inventar traducciones cuando el contexto sea insuficiente.
- Marcar como `fuzzy` cualquier traducción dudosa.

Conservar exactamente:

- placeholders (`%s`, `%d`, `%(name)s`, `{}`, `{name}`, etc.);
- etiquetas HTML;
- etiquetas XML;
- expresiones QWeb;
- saltos de línea;
- espacios significativos;
- identificadores técnicos;
- nombres de modelos;
- nombres de campos;
- variables;
- expresiones de dominio.

No modificar manualmente las referencias técnicas generadas automáticamente dentro del archivo `.po`, salvo cuando el proceso normal de actualización las modifique.

---

# Restricciones

Durante tareas de traducción NO modificar:

- modelos;
- campos;
- vistas;
- acciones;
- menús;
- reportes;
- asistentes;
- ACL;
- reglas de seguridad;
- lógica de negocio;
- datos;
- archivos XML;
- archivos CSV;
- dependencias;
- versiones del módulo.

No crear, modificar ni eliminar archivos de traducción distintos de:

```
i18n/es_MX.po
```

salvo que la tarea lo solicite explícitamente.

---

# Validación

Validar todos los archivos generados o modificados utilizando:

```bash
msgfmt --check <modulo>/i18n/es_MX.po
```

Corregir cualquier error antes de finalizar.

---

# Reporte final

Al terminar, generar un resumen indicando:

- módulos analizados;
- módulos omitidos;
- archivos `es_MX.po` creados;
- archivos `es_MX.po` actualizados;
- traducciones agregadas;
- traducciones reutilizadas desde archivos existentes;
- traducciones marcadas como `fuzzy`;
- entradas obsoletas;
- errores encontrados;
- resultado de la validación.

---

# Terminología preferida

| Inglés | Español (es_MX) |
|---------|------------------|
| Asset | Activo |
| Resource | Recurso |
| Rental | Renta |
| Quotation | Cotización |
| Sales Order | Orden de venta |
| Purchase Order | Orden de compra |
| Manufacturing Order | Orden de fabricación |
| Project | Proyecto |
| Task | Tarea |
| Timesheet | Hoja de horas |
| Employee | Empleado |
| Vendor | Proveedor |
| Customer | Cliente |
| Company | Empresa |
| Warehouse | Almacén |
| Stock Move | Movimiento de inventario |
| Inventory Adjustment | Ajuste de inventario |
| Bill of Materials | Lista de materiales |
| Work Center | Centro de trabajo |
| Quality Check | Control de calidad |
| Repair Order | Orden de reparación |

---

# Principios generales

- Realizar el menor número posible de cambios.
- Conservar el estilo del proyecto.
- Mantener consistencia entre todos los módulos.
- Antes de finalizar, revisar que las nuevas traducciones sean coherentes con las existentes.
- Nunca reemplazar una traducción correcta únicamente por una preferencia de redacción.