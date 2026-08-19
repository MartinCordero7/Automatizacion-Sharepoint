@echo off
chcp 65001 > nul
set PYTHONUTF8=1

:: Nos ubicamos de forma segura en la carpeta del script
cd /d "%~sdp0"

echo [%date% %time%] === INICIANDO SINCRONIZACION MASIVA === >> historial_sincronizacion.txt

:: -----------------------------------------------------------
:: 1. EJECUCIÓN DE SHAREPOINT
:: -----------------------------------------------------------
echo -> Procesando SharePoint... >> historial_sincronizacion.txt
"C:\Users\esteban.sandoval\AppData\Local\Programs\Python\Python313\python.exe" conexionSharepoint.py >> historial_sincronizacion.txt 2>&1

:: -----------------------------------------------------------
:: 2. EJECUCIÓN DE ORACLE
:: -----------------------------------------------------------
echo -> Procesando Oracle... >> historial_sincronizacion.txt
"C:\Users\esteban.sandoval\AppData\Local\Programs\Python\Python313\python.exe" conexionOracle.py >> historial_sincronizacion.txt 2>&1

echo [%date% %time%] === SINCRONIZACION FINALIZADA === >> historial_sincronizacion.txt
echo ------------------------------------------------- >> historial_sincronizacion.txt