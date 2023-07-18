#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2023 Ángel Alcantar

"""
Este complemento de NVDA proporciona un atajo de teclado para eliminar el proceso enfocado actualmente.
Presione 'Windows + F4' para eliminar el proceso de la ventana actual.This add-on is based on code from the original "winWizard.py" NVDA add-on.
Código original del compelmento de Oriol Gómez.
"""


import api
import winKernel
import ui
import tones
import config
from scriptHandler import script
import globalPluginHandler

class process:
    def __init__(self):
        self.pid = api.getFocusObject().processID

    def kill(self) -> int:
        PROCESS_TERMINATE = 1
        handle = winKernel.kernel32.OpenProcess(PROCESS_TERMINATE, 0, self.pid)
        res = winKernel.kernel32.TerminateProcess(handle, 0)
        winKernel.kernel32.CloseHandle(handle)
        return res

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    @script(
        # Translators: Description of the keyboard command that kills currently focused process.
        description=_("Mata el proceso enfocado actualmente."),
        gesture="kb:windows+f4",
        category = "Kill process"
    )
    def script_killProcess(self, gesture):
        if api.getFocusObject().appModule.productName in ["NVDA", "explorer"]: # Comprobación en modo lista por si se quieren añadir otros procesos críticos que no se desean matar
            ui.message(_("Tiene enfocado un proceso restringido"))
            return
        else:
            p = process()
            res = p.kill()
            if res == 0:
                # Translators: Announced when current process cannot be killed.
                ui.message(_("No se puede matar el proceso actual"))
                return
            else:
                tones.beep(90, 80)
