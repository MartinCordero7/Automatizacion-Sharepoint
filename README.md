# Sistema de Adquisición de Información de OEC (Conexión SharePoint y Oracle a Google Forms/Sheets)

Este proyecto automatiza la extracción de datos desde **SharePoint** y **Oracle** para sincronizarlos directamente en archivos de **Google Sheets**.

---

## 🚀 ¿Cómo hacer que funcione por primera vez? (o en una computadora nueva)

Para que el programa funcione, necesitas configurar dos cosas importantes que, por seguridad, no se suben a GitHub:

1. **El archivo `.env` (Contraseñas de SharePoint y Oracle):**
   Debes crear un archivo llamado `.env` en la misma carpeta que los scripts, con la siguiente estructura:
   ```
   SHAREPOINT_URL=https://tu-url-de-sharepoint
   SHAREPOINT_USER=tu.usuario
   SHAREPOINT_PASSWORD=tu_contraseña_actual
   
   ORACLE_USER=usuario_oracle
   ORACLE_PASSWORD=contraseña_oracle
   ORACLE_DSN=(DESCRIPTION=(ADDRESS=...))
   
   GOOGLE_CREDENTIALS_FILE=nombre-del-archivo-token.json
   ```

2. **El token de Google (Cuenta de Servicio):**
   - Debes colocar el archivo `.json` de la Cuenta de Servicio de Google en la misma carpeta.
   - **¡MUY IMPORTANTE!** Debes abrir el archivo `.json`, copiar el correo electrónico que aparece adentro (suele terminar en `@...iam.gserviceaccount.com`), ir a tus archivos de Google Sheets ("Actividades OI", "Actividades LE", etc.) y **compartirles acceso de "Editor" a ese correo**. Si no lo haces, el script no podrá ver los archivos.

---

## 🛠️ ¿Qué hacer si deja de funcionar? (Guía de Solución de Problemas)

Si el programa venía funcionando bien y de repente falla, revisa el archivo **`historial_sincronizacion.csv`** que se genera automáticamente. Ahí te dirá exactamente dónde ocurrió el error.

Aquí están los problemas más comunes y cómo solucionarlos:

### 1. Error de "Contraseña Inválida" o "Acceso Denegado" en SharePoint u Oracle
- **Causa:** Es muy probable que tu contraseña corporativa haya expirado o la hayas cambiado recientemente.
- **Solución:** Abre el archivo `.env` con el Bloc de notas y actualiza `SHAREPOINT_PASSWORD` u `ORACLE_PASSWORD` con tu contraseña nueva.

### 2. Error `SpreadsheetNotFound` (No encuentra el archivo de Google Sheets)
- **Causa:** La Cuenta de Servicio (el script) no tiene permiso para ver el archivo de Excel. Esto pasa si creaste un archivo nuevo o si alguien eliminó los permisos del script.
- **Solución:** Vuelve a compartir el archivo de Google Sheets con el correo de la Cuenta de Servicio dándole permisos de Editor.

### 3. Error `WorksheetNotFound` (No encuentra la pestaña)
- **Causa:** Alguien cambió el nombre de la pestaña (hoja) dentro de Google Sheets (por ejemplo, le puso "Pruebas" en lugar de "Organismos de inspeccion").
- **Solución:** Abre el script `conexionSharepoint.py` o `conexionOracle.py`, busca la sección de "rutas_procesamiento" y asegúrate de que el nombre de la variable `"pestana"` coincida EXACTAMENTE con el nombre de la pestaña en Google Sheets (incluyendo mayúsculas y espacios).

### 4. Error de Oracle: "DPI-1047: Cannot locate a 64-bit Oracle Client library"
- **Causa:** El script `conexionOracle.py` utiliza el modo "Thick" de Oracle, el cual requiere que la ruta del "Instant Client" sea correcta.
- **Solución:** Abre `conexionOracle.py` y verifica que la ruta en `oracledb.init_oracle_client(lib_dir=r"C:\oracle\...")` coincida con la ubicación real de tu cliente de Oracle en esa computadora.

### 5. Falla al ejecutar los scripts (Errores de módulos)
- **Causa:** Faltan librerías de Python.
- **Solución:** Abre la terminal (CMD) e instala las dependencias ejecutando:
  `pip install gspread oracledb office365-rest-python-client python-dotenv`

---

## ⚙️ ¿Cómo se ejecuta?
Simplemente dale doble clic al archivo **`disparador.py`**. Este archivo es el cerebro principal que se encarga de llamar primero a SharePoint, luego a Oracle, y te mostrará el progreso en la consola. Al finalizar te dejará un registro en `historial_sincronizacion.csv`.
