import pythoncom
import re
import csv
from datetime import timedelta
import win32com.client

# === Cargar CSV de suscripciones ===
def cargar_suscripciones(path_csv):
    suscripciones = {}
    with open(path_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            id_sub = row["ID_SUSCRIPCION"].strip().lower()
            suscripciones[id_sub] = {
                "nombre": row["NOMBRE_SUSCRIPCION"].strip(),
                "cliente": row["CLIENTE"].strip()
            }
    return suscripciones

# === Convertir fecha a UTC-5 ===
def ajustar_a_utc5(dt):
    return (dt - timedelta(hours=5)).strftime("%H:%M")

# === Buscar nombre de recurso desde query ===
def extraer_nombre_recurso_de_query(cuerpo):
    query_match = re.search(r"(?i)let\s+(\w+)\s*=\s*\"([^\"]+)\".*?Resource\s*==\s*(\w+|\"[^\"]+\")", cuerpo, re.DOTALL)
    if query_match:
        variable, valor, resource = query_match.groups()
        if '"' in resource:
            return resource.strip('"')
        if resource == variable:
            return valor
    return None

# === Buscar nombre de recurso desde resourceId ===
def extraer_nombre_recurso_desde_resource_id(cuerpo, recurso_valor_previo):
    patrones = [
        r"resourceId\s*=\s*(/[^\s]+)",
        r"(?:resource id)\s*[:\t ]*\s*(/[^\s]+)"
    ]

    for patron in patrones:
        match = re.search(patron, cuerpo, re.IGNORECASE)
        if match:
            ruta = match.group(1).strip()
            partes = ruta.strip().split('/')
            partes = [p for p in partes if p]  # Eliminar elementos vacíos

            if len(partes) >= 3 and partes[0].lower() == "subscriptions":
                id_suscripcion = partes[1].lower()
                nombre_recurso = partes[-1]
                return (
                    id_suscripcion,
                    recurso_valor_previo or nombre_recurso
                )
    return None, recurso_valor_previo

# === Buscar por nombre y suscripción desde texto plano ===
def extraer_nombre_y_suscripcion_texto(cuerpo, recurso_valor_previo, suscripcion_id_valor_previo):
    recurso = re.search(r"Target resource name\s+([^\s]+)", cuerpo)
    suscripcion_id = re.search(r"Subscription ID:\s*([a-f0-9\-]+)", cuerpo, re.IGNORECASE)
    suscripcion_nombre = re.search(r"Subscription name:\s*(.+)", cuerpo) or re.search(r'the Azure subscription\s+(.+?)(?:\s*\.)', cuerpo)
    return (
        recurso_valor_previo or (recurso.group(1) if recurso else None),
        suscripcion_id_valor_previo or (suscripcion_id.group(1).lower() if suscripcion_id else None),
        suscripcion_nombre.group(1).strip() if suscripcion_nombre else None
    )

# === Alias de alerta desde Properties ===
def determinar_alias(nombre_alerta, cuerpo):
    props_match = re.search(r"Properties\s+{(.*?)}", cuerpo, re.DOTALL)
    nombre = nombre_alerta.lower()
    if props_match:
        contenido = props_match.group(1)
        if re.search(r"\b(reboot)\b", contenido, re.IGNORECASE):
            return "reinicio"
        if "unavailable" in contenido.lower():
            return "indisponibilidad"
        if "is starting" in contenido.lower():
            return "inicio"
    if "cpu" in nombre:
        return "CPU"
    if "memory" in nombre or "memoria" in nombre:
        return "memoria"
    if "disk" in nombre or "disco" in nombre:
        return "disco"
    if "create" in nombre or "creacion" in nombre or "creación" in nombre:
        return "creación de recursos"
    if "failed requests" in nombre:
        return "solicitudes fallidas"
    return nombre_alerta

# === Procesar un solo correo ===
def procesar_correo(correo, errores, suscripciones):
    asunto = correo["asunto"]
    cuerpo = correo["cuerpo"]
    remitente = correo["correo_remitente"]
    fecha_utc5 = correo["fecha_objeto"]# - timedelta(hours=5)

    if "microsoft" not in remitente.lower():
        errores.append(f"Correo ignorado (no Microsoft) - Asunto: {asunto} - Fecha: {fecha_utc5.strftime("%Y-%m-%d")} - Hora: {fecha_utc5.strftime("%H:%M")}")
        return (None, errores)

    nombre_alerta = tipo = alias = recurso = id_suscripcion = None
    suscripcion_nombre = cliente = None

    if "Planned Maintenance" in asunto:
        nombre_alerta = "Planned Maintenance"
        alias = "mantenimiento programado"
        tipo = "Otro"
        m = re.search(r"to\s+(.*)", asunto)
        if m:
            recurso = m.group(1).strip()
    elif "budget" in asunto:
        nombre_alerta = "Billing"
        alias = "billing"
        tipo = "Otro"
    else:
        if "Severity:" in asunto:
            nombre_alerta = re.search(r"Severity:\s*\d\s*(.+)", asunto)
            tipo = "Activated" if "Activated" in asunto else "Deactivated" if "Deactivated" in asunto else "Otro"
        if "Alert" in asunto and "was" in asunto and not nombre_alerta:
            nombre_alerta = re.search(r"Alert\s+[\"']?([^\"']+)[\"']?\s+was", asunto)
            nombre_alerta = nombre_alerta or re.search(r"Alert\s+(.*?)\s+was", asunto)
            tipo = "Otro"
        if "alert" in asunto and "was" in asunto and not nombre_alerta:
            nombre_alerta = re.search(r"alert\s+[\"']?([^\"']+)[\"']?\s+was", asunto)
            nombre_alerta = nombre_alerta or re.search(r"alert\s+(.*?)\s+was", asunto)
            tipo = "Otro"

        if not nombre_alerta:
            errores.append(f"No se pudo obtener nombre de alerta para este asunto: {asunto}")
            return (None, errores)

        if not isinstance(nombre_alerta, str):
            nombre_alerta = nombre_alerta.group(1).strip()
    
    # Si aún no se definió alias, intentar inferirlo
    if not alias:
        alias = determinar_alias(nombre_alerta, cuerpo)

    # Buscar nombre de recurso y suscripción
    recurso = recurso or extraer_nombre_recurso_de_query(cuerpo)
    id_suscripcion, recurso = extraer_nombre_recurso_desde_resource_id(cuerpo, recurso)
    recurso, id_suscripcion, suscripcion_nombre = extraer_nombre_y_suscripcion_texto(cuerpo, recurso, id_suscripcion)

    if not suscripcion_nombre and id_suscripcion and id_suscripcion in suscripciones:
        suscripcion_nombre = suscripciones[id_suscripcion]["nombre"]
        cliente = suscripciones[id_suscripcion]["cliente"]
    elif suscripcion_nombre:
        for sub in suscripciones.values():
            if suscripcion_nombre.lower() == sub["nombre"].lower():
                cliente = sub["cliente"]
                break

    if alias == "creación de recursos" or alias == "billing":
        if not alias or not suscripcion_nombre or not cliente:
            errores.append(f"Error al procesar correo - Asunto: {asunto} - Fecha: {fecha_utc5.strftime("%Y-%m-%d")} - Hora: {fecha_utc5.strftime("%H:%M")}")
            return (None, errores)
        asunto_mod = f"Se recibe alerta de {alias} en {suscripcion_nombre} de {cliente}".strip()
    else:
        if not recurso:
            errores.append(f"Error al procesar correo - Asunto: {asunto} - Fecha: {fecha_utc5.strftime("%Y-%m-%d")} - Hora: {fecha_utc5.strftime("%H:%M")}")
            return (None, errores)

        if suscripcion_nombre and cliente:
            asunto_mod = f"Se recibe alerta de {alias} para {recurso} en {suscripcion_nombre} de {cliente}"
        else:
            asunto_mod = f"Se recibe alerta de {alias} para {recurso}"

    return ({
        "asunto_original": asunto,
        "asunto_modificado": asunto_mod,
        "fecha": fecha_utc5.strftime("%Y-%m-%d"),
        "hora": fecha_utc5.strftime("%H:%M"),
        "nombre_alerta": nombre_alerta,
        "tipo": tipo
    }, errores)

def procesar_msgs(rutas, suscripciones_csv):
    suscripciones = cargar_suscripciones(suscripciones_csv)
    resultados = []
    errores = []

    pythoncom.CoInitialize()

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")

        for ruta in rutas:
            try:
                mensaje = outlook.CreateItemFromTemplate(ruta)
                if mensaje.Class == 43:  # MailItem
                    correo_info = {
                        "asunto": mensaje.Subject,
                        "remitente": mensaje.SenderName,
                        "correo_remitente": mensaje.SenderEmailAddress,
                        "destinatario": mensaje.To,
                        "fecha": mensaje.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S"),
                        "fecha_objeto": mensaje.ReceivedTime,
                        "cuerpo": mensaje.Body
                    }
                    resultado, errores = procesar_correo(correo_info, errores, suscripciones)
                    if resultado:
                        resultados.append(resultado)
            except Exception as e:
                errores.append(f"Error al abrir {ruta}: {e}")
        return resultados, errores
    finally:
        pythoncom.CoUninitialize()
