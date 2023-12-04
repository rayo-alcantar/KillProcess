import os
import sys
from po_traductor import PoTraductor
import gettext
import polib
import subprocess

def get_available_languages(directory):
	"""
	Obtiene los idiomas disponibles en un directorio específico.
	
	Args:
		directory (str): Ruta del directorio a explorar.

	Returns:
		list: Lista de códigos de idioma disponibles.
	"""
	languages = []
	for dirpath, dirnames, filenames in os.walk(directory):
		if 'nvda.po' in filenames:
			# Obtiene el nombre del directorio padre como código de idioma
			language = os.path.basename(os.path.dirname(dirpath))
			languages.append(language)
	return languages

def actualizar_po_con_pot(po_file, pot_file, encoding='utf-8'):
	"""
	Actualiza un archivo .po con un archivo .pot.

	Args:
		po_file (str): Ruta del archivo .po a actualizar.
		pot_file (str): Ruta del archivo .pot para actualizar.
		encoding (str, optional): Codificación del archivo. Por defecto 'utf-8'.
	"""
	try:
		po = polib.pofile(po_file, encoding=encoding)
	except Exception as e:
		print(f"Error al procesar el archivo {po_file}: {e}")
		return

	try:
		pot = polib.pofile(pot_file, encoding=encoding)
	except Exception as e:
		print(f"Error al procesar el archivo {pot_file}: {e}")
		return
	po_entries = {entry.msgid: entry for entry in po}
	pot_entries = {entry.msgid: entry for entry in pot}

	cambios = False

	for msgid, pot_entry in pot_entries.items():
		if msgid not in po_entries:
			po.append(pot_entry)
			cambios = True

	if cambios:
		po.save(po_file)
		print(f"Archivo actualizado: {po_file}")
	else:
		print(f"Sin cambios: {po_file}")

def actualiza_po(pot_file, directorio_raiz):
	"""
	Actualiza todos los archivos .po en un directorio raíz con un archivo .pot.

	Args:
		pot_file (str): Ruta del archivo .pot para actualizar.
		directorio_raiz (str): Ruta del directorio raíz donde se encuentran los archivos .po.
	"""
	for root, _, files in os.walk(directorio_raiz):
		for file in files:
			if file.endswith(".po"):
				po_file = os.path.join(root, file)
				actualizar_po_con_pot(po_file, pot_file)

def generar_mo_desde_po(archivo_po, archivo_mo):
	"""
	Genera un archivo .mo a partir de un archivo .po.

	Args:
		archivo_po (str): Ruta del archivo .po.
		archivo_mo (str): Ruta del archivo .mo a crear.
	"""
	try:
		subprocess.run(['msgfmt', '-o', archivo_mo, archivo_po], check=True)
		print(f"Archivo {archivo_mo} creado correctamente.")
	except subprocess.CalledProcessError as e:
		print(f"Error al compilar el archivo .po: {e}")
	except Exception as e:
		print(f"Error al compilar el archivo .po: {e}")

# Para killprocess
# Ruta del archivo .pot para la actualización
fichero_pot = "killProcess.pot"
# Ruta del directorio donde están los archivos de idiomas para la traducción
directorio = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "addon", "locale")

# Actualiza los archivos de idioma con nuevas cadenas, si las hay
actualiza_po(fichero_pot, directorio)

# Obtiene los idiomas disponibles para la traducción
lenguajes = get_available_languages(directorio)

errores = []  # Lista para almacenar los idiomas con errores durante la traducción
for i in lenguajes:
	if i not in ["es"]:  # Aquí se pueden excluir idiomas específicos que no se desean traducir
		print("Traduciendo: %s" % i)
		# Define las rutas de los archivos .po y .mo para cada idioma
		fichero = os.path.join(directorio, i, "LC_MESSAGES", "nvda.po")
		fichero_temp = os.path.join(directorio, i, "LC_MESSAGES", "temp.po")
		fichero_mo = os.path.join(directorio, i, "LC_MESSAGES", "nvda.mo")
		try:
			if os.path.isfile(fichero):
				# Renombra el archivo .po existente para realizar la traducción
				os.rename(fichero, fichero_temp)
				# Crea una instancia del traductor y realiza la traducción
				traductor = PoTraductor(fichero_temp, fichero, mostrar_porcentaje=True, idioma_origen="es", idioma_destino=i)
				traductor.traducir()
				# Elimina el archivo temporal y genera el archivo .mo
				os.remove(fichero_temp)
				generar_mo_desde_po(fichero, fichero_mo)
		except Exception as e:
			print("Error: %s" % e)
			# Agrega el idioma a la lista de errores y restaura el archivo .po original
			errores.append(i)
			os.rename(fichero_temp, fichero)
	else:
		# Si el idioma es español, solo genera el archivo .mo
		fichero = os.path.join(directorio, i, "LC_MESSAGES", "nvda.po")
		fichero_mo = os.path.join(directorio, i, "LC_MESSAGES", "nvda.mo")
		generar_mo_desde_po(fichero, fichero_mo)

# Muestra la cantidad de idiomas con errores y los detalles de los mismos
print("Se han producido {} errores".format(len(errores)))
print(errores)