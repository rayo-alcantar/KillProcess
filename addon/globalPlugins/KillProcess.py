#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2023 Ángel Alcantar

"""
Este complemento de NVDA proporciona un atajo de teclado para eliminar el proceso enfocado actualmente.
Presione 'Windows + F4' para eliminar el proceso de la ventana actual.This add-on is based on code from the original "winWizard.py" NVDA add-on.
Código original del complemento de Oriol Gómez.
"""

#importamos los módulos requeridos y los metemos en un bloque try-except por si alguno no se puede usar, o no esté een el dispositivo.
try:
    import api
    import winKernel
    import ui
    import tones
    from scriptHandler import script
    import globalPluginHandler
    import os
    import appModuleHandler
    import subprocess
#importamos el "logHandler" para poder lanzar el error al log.
    from logHandler import log
except ImportError as e:
    log.error(f"error importing libraries. error details: {e}")

# Definimos la clase Process
class process:
    # Inicializamos la clase con el ID del proceso del objeto que está actualmente enfocado
    def __init__(self):
        # Obtenemos el ID del proceso del objeto que está actualmente enfocado
        self.pid = api.getFocusObject().processID

    # Definimos un método para matar el proceso
    def kill(self) -> int:
        # Constante de Windows que especifica el permiso de terminación del proceso
        PROCESS_TERMINATE = 1  
        # Obtenemos un manejador al proceso
        handle = winKernel.kernel32.OpenProcess(PROCESS_TERMINATE, 0, self.pid)  
        # Intentamos terminar el proceso
        res = winKernel.kernel32.TerminateProcess(handle, 0)  
        # Cerramos el manejador del proceso
        winKernel.kernel32.CloseHandle(handle)  
        # Devolvemos el resultado del intento de terminación
        return res  

# Definimos la clase del complemento global
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    # Definimos un script que mata el proceso enfocado actualmente cuando se presiona la combinación de teclas 'Windows + F4'
    @script(
        # Descripción del comando del teclado que mata el proceso enfocado actualmente
        description=_("Mata el proceso enfocado actualmente."),
        # La combinación de teclas que dispara el script
        gesture="kb:windows+f4",
        # La categoría del script (para propósitos de organización)
        category = "Kill process"
    )
    # El método que se llama cuando se presiona la combinación de teclas
    def script_killProcess(self, gesture):  
        # Verificamos si el proceso enfocado actualmente es un proceso restringido
        if api.getFocusObject().appModule.appName in ["NVDA", "explorer"]:  
            # Notificamos al usuario que está enfocando un proceso restringido
            ui.message(_("Tiene enfocado un proceso restringido"))  
            return
        else:
            # Creamos un nuevo objeto de proceso
            p = process()
            # Intentamos matar el proceso
            res = p.kill()  
            # Si el proceso no pudo ser matado
            if res == 0:  
                # Notificamos al usuario que el proceso no pudo ser matado
                ui.message(_("No se puede matar el proceso actual"))  
                return
            else:
                # Si el proceso fue matado exitosamente, hacemos un sonido de pitido
                tones.beep(90, 80) 

    # Definimos un script que mata todos los procesos bloqueados cuando se presiona la combinación de teclas 'Windows + Control + F4'
    @script(
        # Descripción del comando del teclado que mata los procesos bloqueados
        description=_("Mata los procesos bloqueados (aplicaciones que no responden)."),
        # La combinación de teclas que dispara el script
        gesture="kb:windows+control+f4",
        # La categoría del script (para propósitos de organización)
        category = "Kill process"
    )
    # El método que se llama cuando se presiona la combinación de teclas
    def script_killUnresponsiveProcesses(self, gesture):  
        # Ejecutamos el comando tasklist del sistema operativo
        unresponsiveProcesses = os.popen(r'tasklist /fi "STATUS eq not responding" /fo csv /nh').readlines()
        # Para cada proceso encontrado
        for p in unresponsiveProcesses:
            try:
                # Obtenemos el ID del proceso
                pid = int(p.split('","')[1])
            except IndexError:
                # El comando no devolvió ningún proceso. Se informa al usuario y se termina el script.
                ui.message(_("No se han encontrado procesos bloqueados"))
                return
            # Obtenemos el nombre del proceso
            try:
                appModule = appModuleHandler.getAppModuleFromProcessID(pid)
                try:
                    appName = appModule.productName
                except:
                    appName = appModule.appName
                finally:
                    if not appName: appName = p.split('","')[0][1:]
            except:
                appName = ""
            # Ejecutamos el comando taskkill del sistema operativo
            command = f"taskkill /f /pid{pid} "
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            sp = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=si, text=True)
            stdout, stderr = sp.communicate()
            # Informamos al usuario del resultado
            if stderr:
                # No se pudo cerrar el proceso, se iforma del mensaje de error.
                ui.message(f"{appName}\n{stderr}")
            else:
                # El proceso se ha cerrado correctamente
                ui.message(_(f"{appName} se ha cerrado correctamente"))
