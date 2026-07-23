# Instrucciones para Codex

Este repositorio contiene módulos personalizados para Odoo 19 Community.

## Traducciones

- El idioma objetivo es español de México (`es_MX`).
- Cada directorio que contenga un archivo `__manifest__.py` se considera un módulo de Odoo y debe procesarse de forma independiente.
- Cada módulo debe mantener su propio archivo de traducción en:

  `<nombre_del_modulo>/i18n/es_MX.po`

- No crear un archivo `.po` global para todo el repositorio.
- Si un módulo no contiene el directorio `i18n`, crearlo.
- Si un módulo no contiene el archivo `i18n/es_MX.po`, generarlo con todas las cadenas traducibles del módulo.
- Si el archivo `i18n/es_MX.po` ya existe, actualizarlo conservando las traducciones válidas existentes.
- Incorporar las cadenas traducibles nuevas y eliminar o marcar apropiadamente las entradas obsoletas.
- Mantener intactos los valores `msgid`.
- Traducir únicamente los valores `msgstr`.
- No modificar manualmente las referencias técnicas generadas dentro del archivo `.po`, salvo cuando el proceso normal de actualización las modifique.
- Conservar exactamente:
  - placeholders como `%s`, `%d`, `%(name)s`, `{}` y `{name}`;
  - etiquetas HTML y XML;
  - saltos de línea significativos;
  - nombres técnicos;
  - identificadores;
  - expresiones de dominio;
  - nombres de modelos y campos cuando formen parte de referencias técnicas.
- Revisar el contexto funcional del módulo antes de traducir términos ambiguos.
- Utilizar terminología coherente con Odoo en español de México.
- No inventar traducciones cuando el contexto sea insuficiente.
- Marcar como `fuzzy` las traducciones que requieran revisión humana o reportarlas claramente al finalizar.
- No modificar lógica de negocio durante tareas de traducción.
- No modificar:
  - modelos;
  - campos;
  - vistas;
  - acciones;
  - menús;
  - ACL;
  - reglas de seguridad;
  - datos funcionales;
  - versiones de los módulos;
  - dependencias declaradas en `__manifest__.py`.
- No crear, modificar ni eliminar archivos de traducción distintos de `i18n/es_MX.po`, salvo que la tarea lo solicite explícitamente.
- Validar cada archivo `.po` mediante:

  `msgfmt --check <nombre_del_modulo>/i18n/es_MX.po`

- Al finalizar, generar un reporte que incluya:
  - módulos analizados;
  - archivos `es_MX.po` creados;
  - archivos `es_MX.po` actualizados;
  - traducciones agregadas;
  - traducciones conservadas;
  - entradas sin traducir;
  - entradas marcadas como `fuzzy`;
  - entradas obsoletas;
  - errores de validación.

## Terminología preferida

Utilizar de forma consistente la siguiente terminología cuando el contexto corresponda:

| Inglés | Español (es_MX) |
|--------|------------------|
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
- Cuando exista una traducción oficial de Odoo para un término, utilizarla siempre que sea apropiada para el contexto.
- Si una traducción resulta ambigua, utilizar el contexto del módulo antes de decidir.
- En caso de duda, conservar la traducción existente y reportar la entrada para revisión en lugar de sustituirla arbitrariamente.
