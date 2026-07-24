# Instrucciones para Codex

Este repositorio contiene módulos personalizados para Odoo 19 Community.

## Traducciones

- El idioma objetivo es español de México (`es_MX`).
- Cada directorio que contenga un archivo `__manifest__.py` se considera un módulo de Odoo y debe procesarse de forma independiente.
- Cada módulo debe mantener su propio archivo de traducción en:

  `<nombre_del_modulo>/i18n/es_MX.po`

### Generación y actualización

- No crear un archivo `.po` global para todo el repositorio.
- Si un módulo no contiene el directorio `i18n`, crearlo.
- Si un módulo no contiene el archivo `i18n/es_MX.po`, generarlo.
- Si el archivo `i18n/es_MX.po` ya existe, actualizarlo conservando las traducciones válidas existentes.
- Incorporar las cadenas traducibles nuevas.
- Eliminar o marcar como obsoletas las entradas que ya no existan en el código fuente.
- Mantener intactos los valores `msgid`.
- Traducir únicamente los valores `msgstr`.

### Uso de traducciones existentes

Antes de generar o actualizar `i18n/es_MX.po`, seguir el siguiente orden de prioridad:

1. Utilizar el archivo `i18n/es_MX.po` existente, si está presente.
2. Si existe `i18n/es.po`, utilizarlo como referencia principal.
3. Revisar los demás archivos `.po` disponibles dentro del directorio `i18n`.
4. Utilizar las traducciones oficiales de Odoo cuando existan.
5. Analizar el contexto del código fuente (Python, XML, CSV, reportes, asistentes, manifiesto y demás archivos del módulo).
6. Solo cuando no exista suficiente contexto, generar una traducción nueva.

- No sobrescribir una traducción válida únicamente porque pueda redactarse de otra forma.
- Priorizar siempre la consistencia terminológica.
- En caso de conflicto, el código fuente (`msgid`) tiene prioridad sobre cualquier traducción existente.

### Reglas de traducción

- Revisar el contexto funcional del módulo antes de traducir términos ambiguos.
- Utilizar terminología coherente con Odoo en español de México.
- Cuando exista una traducción oficial de Odoo adecuada para el contexto, utilizarla.
- No inventar traducciones cuando el contexto sea insuficiente.
- Marcar como `fuzzy` las traducciones que requieran revisión humana.
- Conservar exactamente:
  - placeholders como `%s`, `%d`, `%(name)s`, `{}` y `{name}`;
  - etiquetas HTML y XML;
  - saltos de línea significativos;
  - nombres técnicos;
  - identificadores;
  - expresiones de dominio;
  - nombres de modelos y campos cuando formen parte de referencias técnicas.
- No modificar manualmente las referencias técnicas generadas dentro del archivo `.po`, salvo cuando el proceso normal de actualización las modifique.

### Restricciones

Durante tareas de traducción no modificar:

- modelos;
- campos;
- vistas;
- acciones;
- menús;
- ACL;
- reglas de seguridad;
- lógica de negocio;
- datos funcionales;
- dependencias declaradas en `__manifest__.py`;
- versiones de los módulos.

No crear, modificar ni eliminar archivos de traducción distintos de `i18n/es_MX.po`, salvo que la tarea lo solicite explícitamente.

### Validación

Validar cada archivo generado o actualizado mediante:

```bash
msgfmt --check <nombre_del_modulo>/i18n/es_MX.po
```

Corregir cualquier error detectado antes de finalizar.

### Reporte final

Al terminar, generar un reporte que incluya:

- módulos analizados;
- archivos `es_MX.po` creados;
- archivos `es_MX.po` actualizados;
- traducciones agregadas;
- traducciones conservadas;
- entradas marcadas como `fuzzy`;
- entradas obsoletas;
- errores de validación.

## Terminología preferida

Utilizar de forma consistente la siguiente terminología cuando el contexto corresponda:

| Inglés | Español (es_MX) |
|---------|------------------|
| Asset | Activo |
| Resource | Recurso |
| Rental | Renta |
| Quotation | Cotización |
| Sales Order | Pedido de venta |
| Purchase Order | Pedido de compra |
| Manufacturing Order | Orden de fabricación |
| Project | Proyecto |
| Task | Tarea |
| Timesheet | Parte de horas |
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

## Principios generales

- Priorizar siempre la precisión funcional sobre la traducción literal.
- Mantener la terminología consistente entre todos los módulos del repositorio.
- Realizar el menor número posible de cambios fuera del objetivo solicitado.
- Conservar el estilo y formato existentes del proyecto.
- Antes de dar una traducción por finalizada, verificar que sea consistente con el resto del repositorio.
