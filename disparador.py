import sys
import subprocess
import csv
import os
from datetime import datetime

ARCHIVO_LOG = "historial_sincronizacion.csv"

def log_to_csv(script_name, status, details):
    file_exists = os.path.isfile(ARCHIVO_LOG)
    
    # Reemplazamos los saltos de línea por " | " para que todo el texto quede en una sola fila en Excel
    # Así evitamos que la celda se expanda y rompa el formato del archivo.
    details_limpios = details.replace('\n', ' | ').replace('\r', '')
    
    # Usamos utf-8-sig para que Excel reconozca correctamente los acentos y ñ (BOM)
    with open(ARCHIVO_LOG, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # Escribir encabezados si el archivo es nuevo
        if not file_exists:
            writer.writerow(["Fecha y Hora", "Script/Proceso", "Estado", "Detalles"])
            
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        writer.writerow([now, script_name, status, details_limpios])

def main():
    # Mensajes visuales para la consola (ya no estará en negro)
    print("======================================================")
    print("      SISTEMA DE SINCRONIZACIÓN A GOOGLE SHEETS       ")
    print("======================================================")
    print("\n>> Iniciando proceso global...")
    
    log_to_csv("Inicio Global", "OK", "Iniciando proceso de sincronización general")
    
    # 1. Ejecutar el primer script (Sharepoint)
    print("\n[1/2] Ejecutando sincronización de SharePoint...")
    try:
        # Quitamos encoding='utf-8' para evitar el error de los rombos con signos de interrogación
        resultado_sp = subprocess.run(
            [sys.executable, "conexionSharepoint.py"], 
            capture_output=True, 
            text=True
        )
        if resultado_sp.returncode == 0:
            print("      ¡Sincronización de SharePoint exitosa!")
            log_to_csv("conexionSharepoint.py", "Éxito", resultado_sp.stdout.strip())
        else:
            print("      Ocurrió un error en SharePoint (Ver archivo de historial).")
            error_salida = resultado_sp.stderr.strip() if resultado_sp.stderr else resultado_sp.stdout.strip()
            log_to_csv("conexionSharepoint.py", "Error", error_salida)
    except Exception as e:
        print(f"      Error crítico en SharePoint: {e}")
        log_to_csv("conexionSharepoint.py", "Error (Excepción)", str(e))
    
    # 2. Ejecutar el segundo script (Oracle)
    print("\n[2/2] Ejecutando sincronización de Oracle...")
    try:
        resultado_or = subprocess.run(
            [sys.executable, "conexionOracle.py"], 
            capture_output=True, 
            text=True
        )
        if resultado_or.returncode == 0:
            print("      ¡Sincronización de Oracle exitosa!")
            log_to_csv("conexionOracle.py", "Éxito", resultado_or.stdout.strip())
        else:
            print("      Ocurrió un error en Oracle (Ver archivo de historial).")
            error_salida = resultado_or.stderr.strip() if resultado_or.stderr else resultado_or.stdout.strip()
            log_to_csv("conexionOracle.py", "Error", error_salida)
    except Exception as e:
        print(f"      Error crítico en Oracle: {e}")
        log_to_csv("conexionOracle.py", "Error (Excepción)", str(e))
    
    log_to_csv("Fin Global", "OK", "Proceso de sincronización general finalizado")
    
    print("\n======================================================")
    print("               PROCESO FINALIZADO CON ÉXITO           ")
    print("======================================================")
    
if __name__ == "__main__":
    main()
