# Instrucciones para Codex

Este repositorio contiene módulos personalizados y de terceros adaptados para Odoo 19 Community.

## Alcance

Estas instrucciones se aplican a todo el repositorio.

El objetivo es mantener, generar, actualizar y auditar los archivos de traducción al español de México:

```text
<modulo>/i18n/es_MX.po
```

El trabajo no consiste únicamente en completar cadenas vacías. Debe garantizar que cada traducción sea:

* funcionalmente correcta;
* coherente con el lugar donde aparece;
* natural para usuarios de México;
* consistente con la terminología de Odoo 19;
* completa;
* compatible con el cargador de traducciones de Odoo 19.

Una traducción existente nunca debe asumirse correcta únicamente porque:

* `msgstr` no esté vacío;
* no tenga la marca `fuzzy`;
* haya sido generada anteriormente;
* sea gramaticalmente válida de forma aislada;
* coincida con una traducción usada en otro contexto.

Todas las entradas funcionales deben revisarse individualmente y en contexto.

---

# 1. Identificación de módulos

Todo directorio que contenga un archivo:

```text
__manifest__.py
```

se considera un módulo de Odoo.

Los módulos pueden encontrarse en cualquier nivel del repositorio y deben descubrirse recursivamente.

Cada módulo mantiene su propio catálogo:

```text
<modulo>/i18n/es_MX.po
```

Nunca crear un catálogo global compartido entre módulos.

Antes de comenzar, generar un inventario de:

* módulos encontrados;
* módulos instalables;
* módulos no instalables;
* módulos con `i18n/es_MX.po`;
* módulos sin `i18n/es_MX.po`;
* módulos con otros archivos `.po`;
* módulos cuyos manifiestos no puedan analizarse.

No omitir silenciosamente ningún módulo.

---

# 2. Restricciones generales

Durante una tarea exclusivamente de traducción, no modificar:

* modelos Python;
* vistas XML;
* acciones;
* menús;
* controladores;
* lógica de negocio;
* ACL;
* reglas de registro;
* archivos CSV;
* datos;
* pruebas;
* versiones de módulos;
* manifiestos;
* documentación;
* recursos estáticos.

Solo se permite crear o modificar:

```text
<modulo>/i18n/es_MX.po
```

salvo que la tarea solicite expresamente otros cambios.

No cambiar cadenas fuente para facilitar su traducción.

No eliminar entradas válidas únicamente porque no se haya localizado inmediatamente su uso.

No reformatear masivamente archivos `.po` sin necesidad.

---

# 3. Conservación de nombres propios y productos

No traducir automáticamente:

* marcas;
* nombres comerciales;
* nombres de productos;
* nombres de suites;
* nombres registrados;
* nombres propios de empresas;
* nombres de módulos cuando funcionan como identidad comercial;
* acrónimos reconocibles;
* tecnologías;
* nombres de protocolos;
* nombres de bibliotecas o plataformas.

Ejemplos que deben conservarse:

```text
Open HRMS
Open HRMS Core
Odoo
GitHub
PostgreSQL
Python
QWeb
OWL
REST
API
URL
UUID
```

Antes de traducir el nombre visible de un módulo, determinar si corresponde a:

1. una descripción funcional traducible;
2. un nombre comercial no traducible;
3. un nombre mixto.

Para nombres mixtos, conservar la marca y traducir solo la parte descriptiva cuando resulte natural.

Ejemplos:

```text
Open HRMS Core
```

Debe permanecer:

```text
Open HRMS Core
```

Un nombre como:

```text
Open HRMS Employee Transfer
```

podría traducirse como:

```text
Open HRMS - Transferencia de empleados
```

solo si el contexto confirma que la parte posterior es descriptiva y no forma parte del nombre oficial del producto.

Ante duda razonable, conservar el nombre original y documentarlo en el reporte final.

---

# 4. Fuentes de referencia

Antes de modificar una traducción, consultar en este orden:

1. las referencias `#:` de la entrada;
2. el archivo Python, XML, JavaScript, QWeb o manifiesto referenciado;
3. el tipo de elemento funcional donde aparece;
4. otros usos del mismo `msgid` dentro del módulo;
5. `i18n/es_MX.po`;
6. `i18n/es.po`;
7. otros archivos `.po` del mismo módulo;
8. traducciones oficiales de Odoo 19;
9. terminología usada por módulos relacionados del repositorio;
10. una traducción nueva razonada por Codex.

Las traducciones existentes deben conservarse cuando sean correctas en su contexto.

No deben conservarse si contienen:

* Spanglish;
* traducciones incompletas;
* inglés residual no justificado;
* errores gramaticales;
* terminología funcional incorrecta;
* traducciones literales poco naturales;
* errores de género o número;
* inconsistencias entre módulos;
* significados incorrectos para el control donde aparecen;
* traducciones que alteren el comportamiento percibido;
* nombres comerciales traducidos indebidamente.

---

# 5. Reconstrucción obligatoria del contexto

Para cada entrada funcional, identificar cuando sea posible:

* módulo;
* archivo fuente;
* modelo;
* campo;
* vista;
* menú;
* acción;
* botón;
* estado;
* selección;
* mensaje;
* informe;
* plantilla;
* código JavaScript;
* nombre visible del módulo.

No traducir una cadena únicamente a partir del `msgid` cuando las referencias permitan reconstruir su uso.

## 5.1 Campos y etiquetas

Revisar:

* nombre técnico del campo;
* modelo al que pertenece;
* tipo de campo;
* ayuda del campo;
* vista en la que aparece;
* relación con otros campos.

Ejemplo:

```text
State
```

Puede significar:

* Estado, como situación de un registro;
* Estado, como entidad territorial;
* condición;
* etapa.

Debe elegirse según el modelo y el uso real.

## 5.2 Botones y acciones

Los botones deben traducirse preferentemente como acciones claras y naturales.

Ejemplos:

```text
Confirm
```

Puede ser:

```text
Confirmar
```

```text
Validate
```

Puede ser:

```text
Validar
```

No traducir ambos indiscriminadamente como la misma acción si Odoo distingue funcionalmente entre confirmar, validar, aprobar o publicar.

## 5.3 Estados y valores de selección

Los estados deben leerse como condiciones del registro, no necesariamente como órdenes.

Ejemplo:

```text
Cancelled
```

Como estado:

```text
Cancelado
```

No:

```text
Cancelar
```

Revisar género y número según la entidad:

* Cancelado;
* Cancelada;
* Cancelados;
* Canceladas.

Cuando la misma cadena se utilice para entidades con géneros incompatibles, evitar una solución forzada. Conservar la mejor traducción compatible con el uso dominante y documentar la ambigüedad.

## 5.4 Menús, acciones y encabezados

Traducir como nombres de áreas funcionales, no como frases literales.

Ejemplo:

```text
Purchase Orders
```

Normalmente:

```text
Órdenes de compra
```

No:

```text
Pedidos de adquisición
```

## 5.5 Mensajes de validación y errores

Conservar:

* sentido técnico;
* condición que provocó el error;
* acción que debe realizar el usuario;
* placeholders;
* saltos de línea necesarios.

No suavizar ni abreviar un mensaje de forma que pierda información funcional.

## 5.6 Textos de ayuda y descripciones

Usar español natural de México.

Evitar estructuras calcadas del inglés, especialmente:

* abuso de gerundios;
* sustantivos encadenados;
* voz pasiva innecesaria;
* mayúsculas en cada palabra;
* anglicismos evitables.

## 5.7 Cadenas con múltiples referencias

Cuando un mismo `msgid` tenga varias referencias, revisar todas antes de traducir.

No asumir que una traducción válida para una referencia será válida para las demás.

Si los contextos requieren traducciones incompatibles y Odoo los agrupa en una sola entrada:

* no modificar el código fuente durante esta tarea;
* elegir la traducción menos ambigua y más segura;
* registrar el conflicto en el reporte final;
* indicar las referencias afectadas.

---

# 6. Terminología de Odoo

Utilizar prioritariamente la terminología habitual de Odoo 19 en español.

| Inglés                | Español de México        |
| --------------------- | ------------------------ |
| Sales Order           | Orden de venta           |
| Purchase Order        | Orden de compra          |
| Manufacturing Order   | Orden de fabricación     |
| Delivery Order        | Orden de entrega         |
| Stock Move            | Movimiento de inventario |
| Work Order            | Orden de trabajo         |
| Project               | Proyecto                 |
| Task                  | Tarea                    |
| Timesheet             | Hoja de horas            |
| Employee              | Empleado                 |
| Customer              | Cliente                  |
| Vendor                | Proveedor                |
| Warehouse             | Almacén                  |
| Bill of Materials     | Lista de materiales      |
| Inventory Adjustment  | Ajuste de inventario     |
| Journal Entry         | Asiento contable         |
| Payment Terms         | Condiciones de pago      |
| Pricelist             | Lista de precios         |
| Asset                 | Activo                   |
| Resource              | Recurso                  |
| Rental                | Renta                    |
| Quotation             | Cotización               |
| Contact               | Contacto                 |
| Fiscal Position       | Posición fiscal          |
| Analytic Account      | Cuenta analítica         |
| Analytic Distribution | Distribución analítica   |
| Picking               | Transferencia            |
| Receipt               | Recepción                |
| Scrap                 | Desecho                  |
| Replenishment         | Reabastecimiento         |
| Lead                  | Iniciativa               |
| Opportunity           | Oportunidad              |
| Stage                 | Etapa                    |

Esta tabla es una guía, no una sustitución del análisis contextual.

Cuando el contexto lo requiera, adaptar la traducción.

Ejemplos:

```text
Partner
```

Puede significar:

* Contacto;
* Cliente;
* Proveedor;
* Empresa;
* Persona de contacto.

```text
Move
```

Puede significar:

* Movimiento de inventario;
* Asiento contable;
* traslado;
* mover.

```text
Order
```

Puede significar:

* Orden;
* pedido;
* secuencia;
* ordenar.

No aplicar glosarios de forma mecánica.

---

# 7. Español de México

Priorizar:

1. precisión funcional;
2. consistencia con Odoo;
3. claridad para el usuario;
4. naturalidad en español de México.

Evitar:

* Spanglish;
* traducciones parciales;
* anglicismos innecesarios;
* calcos sintácticos;
* traducciones palabra por palabra;
* lenguaje excesivamente peninsular cuando exista una forma habitual en México;
* abreviaturas no documentadas;
* mayúsculas innecesarias.

Usar mayúscula inicial normal, no estilo de título inglés, salvo nombres propios.

Ejemplo:

```text
Manufacturing Process Costing
```

Preferir:

```text
Costeo del proceso de fabricación
```

No:

```text
Costeo Del Proceso De Fabricación
```

---

# 8. Elementos que deben conservarse exactamente

No modificar ni traducir:

* placeholders;
* nombres de variables;
* expresiones QWeb;
* etiquetas HTML;
* entidades HTML;
* atributos XML;
* identificadores técnicos;
* dominios;
* expresiones Python;
* fragmentos JavaScript;
* comandos;
* rutas;
* nombres de modelos;
* nombres técnicos de campos cuando aparezcan como código.

Conservar exactamente, entre otros:

```text
%s
%d
%r
%(name)s
%(count)d
{name}
{count}
{}
{0}
{1}
${name}
<t>
</t>
```

Conservar también:

* cantidad;
* tipo;
* nombre;
* orden;
* formato;
* duplicación intencional de placeholders.

Una traducción con placeholders alterados debe considerarse inválida aunque `msgfmt` no la rechace.

---

# 9. Plurales

Conservar correctamente las estructuras:

```po
msgid ""
msgid_plural ""
msgstr[0] ""
msgstr[1] ""
```

No convertir entradas plurales en entradas simples.

Verificar que ambas formas estén traducidas.

Para `es_MX`, usar las reglas plurales correctas del encabezado del catálogo.

No copiar automáticamente plurales desde idiomas con reglas diferentes.

---

# 10. Generación y actualización de catálogos

## 10.1 Regla fundamental

Las referencias de ocurrencia `#:` deben ser generadas por Odoo o por herramientas compatibles con la versión objetivo.

Nunca inventar, reescribir o normalizar manualmente metadatos de ocurrencia sin comprobar que Odoo 19 los acepta.

No generar referencias antiguas o incompatibles como:

```text
#: model_terms:static/src/xml/...
#: model_terms:views/...
#: code:models/archivo.py
```

Las referencias deben conservar el formato generado por Odoo 19, por ejemplo:

```text
#: model_terms:ir.ui.view,arch_db:modulo.identificador
#: code:addons/modulo/ruta/archivo.py:0
```

El formato exacto debe provenir de la herramienta de exportación, no de una transformación manual.

## 10.2 Catálogo existente

Si existe `i18n/es_MX.po`:

1. validar primero su sintaxis;
2. obtener o generar una plantilla POT compatible con Odoo 19;
3. actualizar mediante una herramienta como `msgmerge`;
4. preservar traducciones correctas;
5. revisar las entradas nuevas;
6. revisar todas las traducciones existentes;
7. revisar entradas obsoletas antes de eliminarlas;
8. validar el resultado.

Nunca reconstruir completamente un catálogo válido si puede actualizarse de manera segura.

Sin embargo, si el archivo contiene metadatos incompatibles con Odoo 19, reconstruir su estructura desde una plantilla exportada por Odoo 19 y fusionar las traducciones existentes.

## 10.3 Catálogo inexistente

Si no existe `i18n/es_MX.po`:

1. crear `i18n/` si es necesario;
2. generar una plantilla desde Odoo 19 o desde un procedimiento compatible;
3. crear el catálogo `es_MX.po`;
4. traducir todas las entradas funcionales;
5. validar sintaxis, referencias y placeholders.

No crear un archivo vacío como sustituto de una exportación real.

## 10.4 Requisito del entorno

Antes de exportar traducciones, confirmar:

* versión exacta de Odoo;
* `addons_path`;
* base de datos utilizada;
* que el módulo sea reconocible por Odoo;
* que sus dependencias estén disponibles;
* que el módulo sea instalable;
* que el comando de exportación acepte el módulo.

No asumir que un fallo de exportación significa que el archivo PO está dañado.

Distinguir expresamente entre:

* módulo no instalado;
* módulo no registrado;
* dependencia faltante;
* módulo fuera de `addons_path`;
* manifiesto inválido;
* error de exportación;
* error del catálogo.

No instalar ni actualizar módulos en una base de datos productiva salvo instrucción expresa.

---

# 11. Revisión obligatoria de todas las entradas

Para cada `msgid`:

1. leer las referencias;
2. localizar el origen;
3. determinar el tipo de elemento;
4. revisar el contexto funcional;
5. revisar el `msgstr`;
6. comprobar terminología;
7. comprobar naturalidad;
8. comprobar marcas y nombres propios;
9. comprobar placeholders;
10. comprobar género, número y modo verbal;
11. corregir si es necesario;
12. retirar `fuzzy` solo después de validar la traducción.

No revisar únicamente:

* cadenas vacías;
* entradas `fuzzy`;
* entradas nuevas;
* entradas que contengan palabras inglesas.

No declarar un módulo como revisado si no se inspeccionaron todas sus entradas funcionales.

---

# 12. Detección de traducciones sospechosas

Buscar activamente:

* `msgstr` vacío;
* entradas `fuzzy`;
* `msgstr` idéntico al `msgid`;
* palabras inglesas residuales;
* traducciones parcialmente en inglés;
* marcas traducidas;
* mayúsculas tipo título;
* dobles espacios;
* espacios antes de signos;
* puntuación inconsistente;
* traducciones excesivamente literales;
* placeholders diferentes;
* etiquetas HTML alteradas;
* traducciones duplicadas inconsistentes;
* estados expresados como infinitivos;
* botones expresados como estados;
* términos distintos para el mismo concepto;
* términos iguales para conceptos diferentes.

Una coincidencia entre `msgid` y `msgstr` no siempre es un error. Puede ser válida para:

* marcas;
* acrónimos;
* términos técnicos;
* nombres propios;
* palabras iguales en ambos idiomas.

Cada caso debe evaluarse individualmente.

---

# 13. Validación obligatoria

Antes de finalizar, ejecutar para cada catálogo modificado:

```bash
msgfmt --check <modulo>/i18n/es_MX.po
```

Además, verificar:

* integridad de placeholders;
* pluralización;
* encabezado PO;
* codificación UTF-8;
* entradas `fuzzy`;
* entradas vacías;
* traducciones parciales;
* palabras inglesas sospechosas;
* referencias `#:` compatibles con Odoo 19;
* duplicados;
* sintaxis del catálogo.

Cuando haya acceso a un entorno Odoo 19 adecuado, realizar también una validación de carga real:

1. actualizar únicamente los módulos afectados;
2. iniciar Odoo con `--stop-after-init`;
3. revisar el log;
4. buscar específicamente:

```text
malformed po file
unknown occurrence
ValueError
Traceback
ERROR
CRITICAL
```

5. verificar el endpoint de traducciones;
6. comprobar visualmente una muestra representativa.

No usar `--update all` salvo que la tarea lo solicite expresamente y exista una justificación.

Preferir actualizar únicamente los módulos modificados.

---

# 14. Validación visual y funcional

Cuando sea posible, seleccionar una muestra representativa por módulo que incluya:

* nombre visible del módulo;
* menú principal;
* acción;
* formulario;
* lista;
* campo;
* botón;
* estado;
* mensaje de error;
* ayuda;
* informe o asistente.

La validación visual debe comprobar:

* que el texto aparece donde se esperaba;
* que tiene sentido en ese control;
* que no queda cortado de forma problemática;
* que género y número son correctos;
* que un botón describe una acción;
* que un estado describe una condición;
* que no se tradujeron marcas;
* que no queda inglés residual injustificado.

Si no existe acceso a una interfaz ejecutable, declararlo explícitamente. No afirmar que una traducción fue validada visualmente si solo se revisó el código.

---

# 15. Manejo de incertidumbre

Cuando el contexto no permita decidir con seguridad:

1. ampliar la búsqueda en el módulo;
2. revisar modelos y vistas relacionados;
3. buscar el mismo término en Odoo 19;
4. revisar módulos dependientes;
5. conservar temporalmente la traducción más segura;
6. registrar la entrada como ambigua.

No inventar contexto.

No presentar una inferencia como certeza.

El reporte debe incluir:

* módulo;
* `msgid`;
* traducción propuesta;
* referencias;
* motivo de la ambigüedad;
* decisión adoptada.

---

# 16. Estrategia de trabajo

La auditoría debe realizarse en fases.

## Fase 1 — Inventario

* descubrir módulos;
* localizar catálogos;
* identificar archivos ausentes;
* validar encabezados;
* detectar errores estructurales.

## Fase 2 — Actualización técnica

* generar o actualizar plantillas;
* fusionar catálogos;
* corregir metadatos incompatibles;
* preservar traducciones válidas;
* generar catálogos faltantes.

## Fase 3 — Auditoría contextual

* revisar todas las entradas;
* localizar cada uso;
* clasificar el tipo de interfaz;
* corregir traducciones;
* conservar marcas y productos.

## Fase 4 — Consistencia transversal

* comparar terminología entre módulos;
* revisar conceptos recurrentes;
* eliminar variantes injustificadas;
* documentar excepciones contextuales.

## Fase 5 — Validación

* ejecutar `msgfmt --check`;
* verificar placeholders;
* verificar fuzzy;
* verificar inglés residual;
* validar carga en Odoo cuando sea posible.

## Fase 6 — Reporte

* resumir resultados;
* documentar ambigüedades;
* indicar limitaciones;
* enumerar validaciones ejecutadas.

No mezclar una refactorización general del repositorio con esta tarea.

---

# 17. Reporte final obligatorio

Al terminar, indicar:

* módulos descubiertos;
* módulos analizados;
* módulos omitidos;
* motivo de cada omisión;
* archivos creados;
* archivos actualizados;
* archivos reconstruidos;
* traducciones nuevas;
* traducciones modificadas;
* traducciones conservadas;
* traducciones reutilizadas;
* marcas o productos preservados;
* nombres visibles corregidos;
* entradas ambiguas;
* conflictos de contexto;
* entradas `fuzzy` eliminadas;
* entradas `fuzzy` restantes;
* cadenas vacías restantes;
* errores encontrados;
* advertencias encontradas;
* resultado de `msgfmt --check` por módulo;
* resultado de validación de placeholders;
* resultado de carga en Odoo, si se ejecutó;
* limitaciones de la revisión.

Incluir una tabla por módulo con al menos:

| Módulo | Estado inicial | Archivo creado/actualizado | Entradas revisadas | Modificadas | Fuzzy restantes | Validación |
| ------ | -------------- | -------------------------- | -----------------: | ----------: | --------------: | ---------- |

No declarar éxito total si:

* algún catálogo modificado no pasa `msgfmt --check`;
* existen placeholders alterados;
* quedan errores de carga;
* no se revisaron todas las entradas funcionales;
* quedaron módulos sin analizar y no se documentaron;
* se desconoce si las referencias son compatibles con Odoo 19.

---

# 18. Principios generales

* Revisar todas las traducciones existentes.
* Preservar únicamente las traducciones correctas.
* Corregir cualquier error detectado.
* Mantener consistencia entre módulos.
* Usar terminología de Odoo 19.
* Evitar Spanglish.
* Evitar traducciones mecánicas.
* Mantener español natural de México.
* Conservar marcas y nombres comerciales.
* Analizar botones como acciones.
* Analizar estados como condiciones.
* Determinar el significado por contexto.
* No alterar placeholders.
* No inventar referencias de ocurrencia.
* No confundir fallos de exportación con fallos del catálogo.
* No declarar una entrada como revisada sin inspeccionar su uso funcional.
* No declarar validación visual si no se ejecutó la interfaz.
* Priorizar exactitud sobre velocidad.
