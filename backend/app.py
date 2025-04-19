from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
from parse import procesar_msgs
from group import agrupar_por_fecha
from collections import defaultdict

archivos_por_sesion = defaultdict(list)

app = Flask(__name__)
app.secret_key = 'clave_super_secreta'
CORS(app, supports_credentials=True)

# Estructura en memoria para mantener los archivos cargados por sesión
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

@app.route('/subir-archivos', methods=['POST'])
def subir_archivos():
    if 'archivos' not in request.files:
        return jsonify({'error': 'No se encontraron archivos'}), 400

    archivos = request.files.getlist('archivos')
    guardados = []
    errores = []

    for archivo in archivos:
        if archivo.filename.endswith('.msg'):
            nombre_seguro = secure_filename(archivo.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombre_seguro)
            archivo.save(ruta)
            guardados.append(ruta)
        else:
            errores.append(f"Archivo ignorado: {archivo.filename}")

    session_id = session.get('id')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        session['id'] = session_id

    archivos_por_sesion[session_id] = guardados
    return jsonify({'mensaje': 'Archivos subidos correctamente', 'errores': errores, 'id': session_id, 'guardados': guardados})

@app.route('/procesar-correos', methods=['POST'])
def procesar_correos():
    session_id = session.get('id')
    rutas = archivos_por_sesion.get(session_id, [])
    if not rutas:
        return jsonify({'error': 'No hay archivos subidos', 'id': session_id, 'guardados': rutas}), 400

    suscripciones_csv = os.path.join("suscripciones.csv")
    correos, errores = procesar_msgs(rutas, suscripciones_csv)
    resultados_por_fecha = agrupar_por_fecha(correos)

    session.pop('archivos_subidos', None)
    return jsonify({"resultados": resultados_por_fecha, "errores": errores})

@app.route('/restablecer', methods=['POST'])
def restablecer():
    session.pop('archivos_subidos', None)
    return jsonify({'mensaje': 'Archivos reiniciados'})

if __name__ == '__main__':
    app.run(debug=True)
