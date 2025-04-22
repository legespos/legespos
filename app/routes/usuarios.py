from flask import Blueprint, request, jsonify
from app.db import get_db_connection
from werkzeug.security import generate_password_hash
from flask import render_template

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/', methods=['POST'])
def crear_usuario():
    data = request.get_json()

    # Validar presencia de campos requeridos
    campos = ['nombre', 'apellido', 'correo', 'contrasena', 'rol_id']
    for campo in campos:
        if campo not in data or not data[campo]:
            return jsonify({"error": f"El campo '{campo}' es obligatorio."}), 400

    nombre = data['nombre']
    apellido = data['apellido']
    correo = data['correo']
    contrasena_plana = data['contrasena']
    rol_id = data['rol_id']

    # Validar longitud mínima de la contraseña
    if len(contrasena_plana) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres."}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Verificar si el correo ya existe
            cur.execute("SELECT 1 FROM usuarios WHERE correo = %s AND activo = TRUE", (correo,))
            if cur.fetchone():
                return jsonify({"error": "El correo ya está registrado."}), 409

            # Hashear la contraseña
            hashed = generate_password_hash(contrasena_plana)

            # Insertar nuevo usuario
            cur.execute("""
                INSERT INTO usuarios (nombre, apellido, correo, contrasena, rol_id, activo, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
                RETURNING id, nombre, apellido, correo, rol_id, activo, fecha_creacion
            """, (nombre, apellido, correo, hashed, rol_id))

            nuevo_usuario = cur.fetchone()
            conn.commit()

        keys = ['id', 'nombre', 'apellido', 'correo', 'rol_id', 'activo', 'fecha_creacion']
        return jsonify(dict(zip(keys, nuevo_usuario))), 201

    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    
@usuarios_bp.route('/', methods=['GET'])
def listar_usuarios():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.id, u.nombre, u.apellido, u.correo, u.activo, u.fecha_creacion,
                       r.nombre AS rol_nombre
                FROM usuarios u
                JOIN roles r ON u.rol_id = r.id
                ORDER BY u.fecha_creacion DESC, u.id DESC
            """)
            resultados = cur.fetchall()

        usuarios = []
        keys = ['id', 'nombre', 'apellido', 'correo', 'activo', 'fecha_creacion', 'rol_nombre']
        for fila in resultados:
            usuarios.append(dict(zip(keys, fila)))

        return jsonify(usuarios), 200

    except Exception as e:
        return jsonify({"error": f"Error al obtener los usuarios: {str(e)}"}), 500
    
@usuarios_bp.route('/roles', methods=['GET'])
def obtener_roles():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre FROM roles ORDER BY nombre ASC")
            resultados = cur.fetchall()

        roles = []
        for fila in resultados:
            roles.append({"id": fila[0], "nombre": fila[1]})

        return jsonify(roles), 200

    except Exception as e:
        return jsonify({"error": f"Error al obtener los roles: {str(e)}"}), 500
    
    
@usuarios_bp.route('/listar', methods=['GET'])
def vista_lista_usuarios():
    return render_template('usuarios/index.html')



