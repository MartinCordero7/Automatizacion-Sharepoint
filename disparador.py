import sys
import subprocess
import csv
import os
from datetime import datetime

ARCHIVO_LOG = "historial_sincronizacion.csv"

def log_to_csv(script_name, status, details):
    file_exists = os.path.isfile(ARCHIVO_LOG)
    # Usamos utf-8-sig para que Excel reconozca correctamente los acentos y caracteres especiales (BOM)
    with open(ARCHIVO_LOG, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # Escribir encabezados si el archivo es nuevo
        if not file_exists:
            writer.writerow(["Fecha y Hora", "Script/Proceso", "Estado", "Detalles"])
            
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        writer.writerow([now, script_name, status, details])

def main():
    log_to_csv("Inicio Global", "OK", "Iniciando proceso de sincronización general")
    
    # 1. Ejecutar el primer script (Sharepoint)
    try:
        resultado_sp = subprocess.run(
            [sys.executable, "conexionSharepoint.py"], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if resultado_sp.returncode == 0:
            log_to_csv("conexionSharepoint.py", "Éxito", resultado_sp.stdout.strip())
        else:
            # Si hubo error interno en el script, capturamos stderr o stdout
            error_salida = resultado_sp.stderr.strip() if resultado_sp.stderr else resultado_sp.stdout.strip()
            log_to_csv("conexionSharepoint.py", "Error (Código)", error_salida)
    except Exception as e:
        log_to_csv("conexionSharepoint.py", "Error (Excepción)", str(e))
    
    # 2. Ejecutar el segundo script (Oracle)
    try:
        resultado_or = subprocess.run(
            [sys.executable, "conexionOracle.py"], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if resultado_or.returncode == 0:
            log_to_csv("conexionOracle.py", "Éxito", resultado_or.stdout.strip())
        else:
            error_salida = resultado_or.stderr.strip() if resultado_or.stderr else resultado_or.stdout.strip()
            log_to_csv("conexionOracle.py", "Error (Código)", error_salida)
    except Exception as e:
        log_to_csv("conexionOracle.py", "Error (Excepción)", str(e))
    
    log_to_csv("Fin Global", "OK", "Proceso de sincronización general finalizado")

if __name__ == "__main__":
    main()
