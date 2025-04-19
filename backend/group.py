from collections import defaultdict, deque
from datetime import datetime

def formatear_hora(hora_str):
    dt = datetime.strptime(hora_str, "%H:%M")
    sufijo = "am" if dt.hour < 12 else "pm"
    return f"{hora_str} {sufijo}"

def agrupar_correos(correos):
    agrupados = defaultdict(list)

    # Agrupar por asunto_modificado
    for correo in correos:
        clave = (correo["asunto_modificado"], correo["nombre_alerta"])
        agrupados[clave].append(correo)

    resultado_final = defaultdict(list)

    for (asunto_modificado, nombre_alerta), mensajes in agrupados.items():
        mensajes.sort(key=lambda x: (x["fecha"], x["hora"]))  # Ordenar cronológicamente

        if all(m["tipo"] == "Otro" for m in mensajes):
            # Agrupar por hora exacta
            contador_por_hora = defaultdict(int)
            for m in mensajes:
                contador_por_hora[m["hora"]] += 1
            for hora, count in sorted(contador_por_hora.items()):
                resultado_final[asunto_modificado].append(
                    f"({count}) {formatear_hora(hora)}"
                )
        else:
            pila = deque()
            pendientes = []

            for m in mensajes:
                if m["tipo"] == "Activated":
                    pila.append(m)
                elif m["tipo"] == "Deactivated":
                    # Buscar pareja para cerrar
                    for i in range(len(pila)):
                        if pila[i]["nombre_alerta"] == m["nombre_alerta"]:
                            activado = pila[i]
                            desactivado = m
                            # Emparejar y eliminar de la pila
                            resultado_final[asunto_modificado].append(
                                f"(2) {formatear_hora(activado['hora'])}-{formatear_hora(desactivado['hora'])}"
                            )
                            pila.remove(activado)
                            break
                    else:
                        # No hay pareja, queda pendiente
                        pendientes.append(m)
                else:
                    # Tipo no esperado
                    pendientes.append(m)

            # Los que no se emparejaron
            for no_emparejado in list(pila) + pendientes:
                resultado_final[asunto_modificado].append(
                    f"(1) {formatear_hora(no_emparejado['hora'])}"
                )

    # Armar salida
    salida = []
    for asunto_modificado, horas in resultado_final.items():
        cadena = f"{asunto_modificado} [{', '.join(horas)}]"
        salida.append(cadena)

    return salida


def agrupar_por_fecha(correos):
    agrupado_por_fecha = defaultdict(lambda: defaultdict(list))

    # Agrupar por fecha y asunto_modificado
    for correo in correos:
        fecha = correo["fecha"]
        asunto = correo["asunto_modificado"]
        agrupado_por_fecha[fecha][asunto].append(correo)

    resultado = {}

    for fecha, asuntos_dict in agrupado_por_fecha.items():
        grupos_ordenados = []

        for asunto, correos_del_asunto in asuntos_dict.items():
            # Determinar la hora más temprana de cualquier correo del grupo
            hora_referencia = min(c["hora"] for c in correos_del_asunto)
            grupos_ordenados.append((hora_referencia, correos_del_asunto))

        # Ordenar los grupos por hora de referencia ascendente
        grupos_ordenados.sort(key=lambda x: x[0])

        # Procesar con la lógica de agrupación y dar formato
        resultado[fecha] = []
        for _, grupo in grupos_ordenados:
            procesado = agrupar_correos(grupo)
            resultado[fecha].extend(procesado)

    return resultado
