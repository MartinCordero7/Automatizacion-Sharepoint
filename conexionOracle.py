import os
import oracledb
import gspread
from dotenv import load_dotenv

load_dotenv()

def sincronizar_oracle_con_forms_oi():
    # 1. Credenciales y Configuración de Oracle
    usuario = os.getenv("ORACLE_USER")
    clave = os.getenv("ORACLE_PASSWORD")
    dsn_tns = os.getenv("ORACLE_DSN")

    # 2. Matriz de Configuración
    rutas_procesamiento = [
        {
            "nombre_proceso": "Centros de Distribución",
            "doc_sheet": "Actividades OI (Respuestas)",
            "pestana": "Oracle"
        }
    ]

    try:
        # ---------------------------------------------------------
        # FASE 1: Autenticación OAuth 2.0 en Google Sheets
        # ---------------------------------------------------------
        print("1. Autenticando en Google Sheets...")
        token_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
        cliente_gspread = gspread.service_account(
            filename=token_file
        )
        print("-> Autenticación en Google exitosa.\n")

        # ---------------------------------------------------------
        # FASE 2: Conexión a Oracle (Thick Mode)
        # ---------------------------------------------------------
        print("2. Inicializando cliente Oracle en Thick mode...")
        oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient-basic-windows.x64-19.32.0.0.0dbru\instantclient_19_32")
        
        print("3. Conectando a la base de datos Oracle...")
        conexion = oracledb.connect(user=usuario, password=clave, dsn=dsn_tns)
        cursor = conexion.cursor()
        print("-> ¡Conexión a Oracle exitosa!\n")

        # ---------------------------------------------------------
        # FASE 3: Procesamiento
        # ---------------------------------------------------------
        for ruta in rutas_procesamiento:
            proceso = ruta["nombre_proceso"]
            doc_destino = ruta["doc_sheet"]
            pestana_destino = ruta["pestana"]
            
            print(f"--- Procesando: {proceso} ---")
            
            try:
                # Consulta SQL para Centros de Distribución (Nombre / Identificador concatenados)
                consulta_sql = """
                    SELECT DISTINCT 
                        CEX_APELLIDO_PATERNO || ' / ' || CDI_IDENTIF AS NOMBRE_ORGANISMO
                    FROM CO.CO_VW_CENTROS_DISTRIB
                    WHERE UPPER(DCA_NOM_VIG) IN ('REGISTRADO', 'SUSPENDIDO', 'EN TRAMITE', 'EN TRÁMITE')
                      AND CEX_APELLIDO_PATERNO IS NOT NULL
                    ORDER BY CEX_APELLIDO_PATERNO || ' / ' || CDI_IDENTIF ASC
                """
                
                # Ejecutamos la consulta (Sin parámetros ya que no filtramos por :actividad)
                cursor.execute(consulta_sql)
                
                # Extraemos los registros
                registros = cursor.fetchall()
                print(f"-> Se extrajeron {len(registros)} registros vigentes de Oracle.")

                # Preparamos la matriz para Sheets (Con encabezados y la segunda fila fija)
                datos_para_sheets = [["NOMBRE_CENTRO_IDENTIFICADOR"]]
                datos_para_sheets.append(["ESTACION DE SERVICIO NUEVA"])
                
                # Agregamos los datos de Oracle a partir de la fila 3
                for fila in registros:
                    # Nos aseguramos de manejar posibles nulos y convertir a lista
                    valor = str(fila[0]) if fila[0] is not None else ""
                    datos_para_sheets.append([valor])

                # ---------------------------------------------------------
                # FASE 4: Escritura en Google Sheets
                # ---------------------------------------------------------
                print(f"-> Abriendo documento: '{doc_destino}', pestaña: '{pestana_destino}'...")
                libro = cliente_gspread.open(doc_destino)
                hoja = libro.worksheet(pestana_destino)
                
                hoja.clear()
                hoja.update(range_name='A1', values=datos_para_sheets)
                print("-> Sincronización en Sheets completada con éxito.\n")
                
            except Exception as error_entidad:
                print(f"->Error procesando la entidad {proceso}: {error_entidad}\n")

        # ---------------------------------------------------------
        # FASE 5: Cierre Seguro
        # ---------------------------------------------------------
        cursor.close()
        conexion.close()
        print("4. Conexión a Oracle cerrada correctamente. Proceso finalizado.")

    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"Error crítico de Base de Datos Oracle:")
        print(f"Código: {error.code}")
        print(f"Mensaje: {error.message}")
    except Exception as e:
        print(f"Error crítico general: {e}")

if __name__ == "__main__":
    sincronizar_oracle_con_forms_oi()