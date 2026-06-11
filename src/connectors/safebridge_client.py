"""
Cliente para la API SafeBridge (Iker)
Valida la integridad de backups utilizando sandboxes aislados (Form-Data)
"""

import requests
import time
import os
from rich.console import Console

class SafeBridgeClient:
    def __init__(self, base_url="http://86.48.24.180:3000"):
        self.base_url = base_url
        self.console = Console()

    def validar_backup(self, backup_path: str, engine: str, database_name: str):
        """
        Envía el archivo backup real mediante HTTP Multipart (form-data)
        y monitorea el reporte asíncrono en tiempo real.
        """
        run_url = f"{self.base_url}/api/v1/validation/run"
        
        # 1. VERIFICACIÓN FÍSICA LOCAL
        if not os.path.exists(backup_path):
            return False, f"Error local: El archivo '{backup_path}' no existe en tu computadora."

        try:
            self.console.print(f"\n[bold cyan][SafeBridge][/bold cyan] Subiendo archivo de backup al VPS remoto...")
            
            # 2. PREPARAR LA SUBIDA MULTIPART (FORM-DATA)
            # Abrimos el archivo en modo binario de lectura ('rb')
            with open(backup_path, 'rb') as f:
                # El archivo debe mandarse obligatoriamente bajo la clave 'file'
                files = {
                    'file': (os.path.basename(backup_path), f, 'application/octet-stream')
                }
                # Datos adicionales del formulario de entrada
                data = {
                    'engine': engine,
                    'database_name': database_name if database_name else ""
                }
                
                # Realizamos el POST usando 'data' y 'files' (Requests aplica multipart/form-data automáticamente)
                response = requests.post(run_url, data=data, files=files, timeout=30)
            
            if response.status_code != 202:
                return False, f"Error del servidor (Código {response.status_code}): {response.text}"
            
            data_json = response.json()
            task_id = data_json.get("task_id")
            self.console.print(f"[bold green]✓ Archivo recibido. Tarea registrada.[/bold green] ID: [white]{task_id}[/white]")
            
            report_url = f"{self.base_url}/api/v1/validation/{task_id}/report"
            self.console.print("[bold yellow]🔄 Procesando y restaurando entorno en Docker Sandbox remoto... Espera un momento.[/bold yellow]")
            
            # 3. BUCLE DE ESPERA REAL (POLLING)
            while True:
                time.sleep(3)
                rep_response = requests.get(report_url, timeout=5)
                
                if rep_response.status_code == 200:
                    rep_data = rep_response.json()
                    status = rep_data.get("status")
                    
                    if status == "completed":
                        # Retornamos el reporte real calculado por el backend en Rust
                        return True, rep_data.get("report")
                    elif status in ["failed", "error"]:
                        # Si falló internamente, extraemos los detalles o logs si vienen adjuntos
                        report = rep_data.get("report")
                        error_msg = f"El sandbox falló. Estado: {status}"
                        if report and report.get("critical_errors"):
                            error_msg += f" -> Errores: {report.get('critical_errors')}"
                        return False, error_msg
                else:
                    return False, f"Error al consultar el estado: {rep_response.status_code}"
                    
        except requests.exceptions.RequestException as e:
            return False, f"No se pudo establecer comunicación con la API: {str(e)}"