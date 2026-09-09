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
        },
        {
            "actividad_sp": "TODAS", 
            "doc_sheet": "Correos OEC",
            "pestana": "OEC"
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
        if actividad_buscada == "TODAS":
            datos_para_sheets = [["NOMBRE_ORGANISMO"]]
        else:
            datos_para_sheets = [["ACTIVIDAD", "NOMBRE_ORGANISMO", "ESTADO"]]
        
        try:
            # Extraemos de SharePoint
            if actividad_buscada == "TODAS":
                # Si queremos todas, solo filtramos por Vigente (o puedes quitar el filtro de Estado0 si deseas)
                consulta_filtro = "Estado0 eq 'Vigente'"
            else:
                consulta_filtro = f"Actividad eq '{actividad_buscada}' and Estado0 eq 'Vigente'"
                
            items = lista.items.filter(consulta_filtro).get_all().execute_query()
            
            registros = []
            vistos = set()
            for item in items:
                nombre = item.properties.get("Title", "Sin Nombre")
                if actividad_buscada == "TODAS":
                    if nombre not in vistos:
                        vistos.add(nombre)
                        registros.append([nombre])
                else:
                    actividad = item.properties.get("Actividad", "Sin Actividad")
                    estado = item.properties.get("Estado0", "Sin Estado")
                    registro_tupla = (actividad, nombre, estado)
                    if registro_tupla not in vistos:
                        vistos.add(registro_tupla)
                        registros.append([actividad, nombre, estado])
            
            # Ordenar alfabéticamente por NOMBRE_ORGANISMO 
            # Para "TODAS", el nombre está en el índice 0. Para el resto, en el índice 1.
            indice_nombre = 0 if actividad_buscada == "TODAS" else 1
            registros.sort(key=lambda x: x[indice_nombre])
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