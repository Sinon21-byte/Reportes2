# Reportes2

Este repositorio mantiene el proyecto Django original y ahora incluye un módulo Android para generar reportes DOCX **offline** usando las mismas plantillas (`reporte.docx` y `reporte2.docx`) con **Chaquopy + Python**.

## Nuevo módulo Android

Ruta: `android-offline/`

Características implementadas:

- App Android en Kotlin con 2 botones:
  - **Reporte Inspección**
  - **Reporte Actividades**
- Ejecución de Python embebido en APK con Chaquopy.
- Reutilización de lógica de generación DOCX con `docxtpl` + `Pillow` (sin Django).
- Copia de plantillas DOCX desde `assets/templates` al almacenamiento interno.
- Generación de DOCX en almacenamiento del teléfono (`getExternalFilesDir/Documents`).
- Botón **Compartir** para enviar el DOCX por WhatsApp, correo, Drive, etc.
- Sin VPS, sin backend, sin internet para generar reportes.

## Estructura relevante

- `android-offline/app/src/main/assets/templates/` (agregar aquí `reporte.docx` y `reporte2.docx` manualmente)
- `android-offline/app/src/main/python/report_generator.py`
- `android-offline/app/src/main/java/com/reportes/offline/MainActivity.kt`


## Plantillas DOCX (no incluidas en git)

Para dejar el PR solo con código/configuración, **no se versionan archivos binarios** en `android-offline`.
Antes de compilar, copia manualmente:

- `core/plantillas/reporte.docx` -> `android-offline/app/src/main/assets/templates/reporte.docx`
- `core/plantillas/reporte2.docx` -> `android-offline/app/src/main/assets/templates/reporte2.docx`

## Requisitos

- Android Studio Iguana o superior.
- SDK Android 34.
- JDK 17.
- (Opcional) Dispositivo físico Android 8+ (API 26+) o emulador.

> Nota: la primera compilación descarga dependencias Gradle y pip usadas por Chaquopy.

## Cómo compilar y probar (paso a paso)

1. Abrir Android Studio.
2. Seleccionar **Open** y elegir la carpeta `android-offline/`.
3. Esperar sincronización Gradle.
4. Conectar un dispositivo Android o abrir un emulador.
5. Ejecutar la app (`Run > Run 'app'`).
6. En la app:
   - Tocar **Reporte Inspección** para generar un DOCX de inspección con datos dummy.
   - Tocar **Reporte Actividades** para generar un DOCX de actividades con datos dummy.
   - Revisar la ruta mostrada en pantalla.
   - Tocar **Compartir** y elegir WhatsApp/Correo/Drive.

## Dónde queda el archivo DOCX

La app guarda los documentos en:

`Android/data/com.reportes.offline/files/Documents/`

El nombre se genera con timestamp, por ejemplo:

- `reporte_inspeccion_20260222_101500.docx`
- `reporte_actividades_20260222_101520.docx`

## Cómo adaptar de dummy a datos reales

Editar `report_generator.py`:

- `_inspection_context(...)`
- `_activities_context(...)`

y reemplazar valores fijos por datos capturados en UI.

## Nota de compatibilidad

Este módulo Android es independiente del Django web. El backend no es necesario para generar los reportes en móvil.
