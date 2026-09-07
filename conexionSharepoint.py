import os
import sys
sys.path.insert(0, r"C:\Users\esteban.sandoval\libs")
import gspread
from dotenv import load_dotenv
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

load_dotenv()

def sincronizar_sharepoint_con_forms():
    
    url_sitio = os.getenv("SHAREPOINT_URL")
    usuario = os.getenv("SHAREPOINT_USER") 
    password = os.getenv("SHAREPOINT_PASSWORD")
    
    # Mapa de configuración: Aquí vinculamos lo que buscamos en SharePoint con su destino en Sheets
   # Mapa de configuración con los nombres exactos confirmados
    rutas_procesamiento = [
        {
            "actividad_sp": "Organismos de Inspección", 
            "doc_sheet": "Actividades OI (Respuestas)",
            "pestana": "Organismos de inspeccion"
        },
        {
            "actividad_sp": "Laboratorio de Ensayo", 
            "doc_sheet": "Actividades LE (Respuestas)",
            "pestana": "Laboratorios de ensayo"
        },
        {
            "actividad_sp": "Laboratorio de Calibración", 
            "doc_sheet": "Actividades LC (Respuestas)",
            "pestana": "Laboratorios de calibracion"
        }
    ]
    
    # 1. Autenticamos una sola vez en SharePoint
    try:
        print("1. Conectando a SharePoint...")
        ctx = ClientContext(url_sitio)
        ctx.authentication_context._allow_ntlm = True
        ctx.with_credentials(UserCredential(usuario, password))
        lista = ctx.web.lists.get_by_title("OECC Datos Generales")
    except Exception as e:
        print(f"Error crítico al conectar a SharePoint: {e}")
        return 
  
    # 2. Autenticamos una sola vez en Google Sheets
    try:
        print("2. Conectando a Google Sheets...")
        token_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
        cliente_gspread = gspread.service_account(
            filename=token_file
        )
    except Exception as e:
        print(f"Error crítico al conectar a Google Sheets: {e}")
        return

    # 3. Procesamos cada entidad de nuestro mapa de configuración
    for ruta in rutas_procesamiento:
        actividad_buscada = ruta["actividad_sp"]
        doc_destino = ruta["doc_sheet"]
        pestana_destino = ruta["pestana"]
        
        print(f"\n--- Procesando: {actividad_buscada} ---")
        datos_para_sheets = [["ACTIVIDAD", "NOMBRE_ORGANISMO", "ESTADO"]]
        
        try:
            # Extraemos de SharePoint
            consulta_filtro = f"Actividad eq '{actividad_buscada}' and Estado0 eq 'Vigente'"
            items = lista.items.filter(consulta_filtro).get().execute_query()
            
            registros = []
            for item in items:
                nombre = item.properties.get("Title", "Sin Nombre")
                actividad = item.properties.get("Actividad", "Sin Actividad")
                estado = item.properties.get("Estado0", "Sin Estado")
                registros.append([actividad, nombre, estado])
            
            # Ordenar alfabéticamente por NOMBRE_ORGANISMO (índice 1)
            registros.sort(key=lambda x: x[1])
            datos_para_sheets.extend(registros)
                
            print(f"-> ¡Éxito! Se extrajeron {len(datos_para_sheets) - 1} registros vigentes.")
            
            # Escribimos en el archivo y pestaña específicos de Google Sheets
            print(f"-> Actualizando archivo '{doc_destino}', pestaña '{pestana_destino}'...")
            hoja = cliente_gspread.open(doc_destino).worksheet(pestana_destino)
            hoja.clear() 
            hoja.update(range_name='A1', values=datos_para_sheets) 
            print("-> ¡Sincronización de esta entidad completada!")
            
        except Exception as e:
            # Si una entidad falla (por ejemplo, alguien le cambia el nombre al archivo de Sheets),
            # capturamos el error para que el script no se detenga y continúe con la siguiente.
            import traceback
            print(f"Error al procesar la ruta de {actividad_buscada}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    sincronizar_sharepoint_con_forms()