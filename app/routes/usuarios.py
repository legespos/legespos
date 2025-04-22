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
    
@usuarios_bp.route('/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    data = request.get_json()
    campos_actualizables = ['nombre', 'apellido', 'correo', 'contrasena', 'rol_id']
    valores = {}

    for campo in campos_actualizables:
        if campo in data and data[campo]:
            valores[campo] = data[campo]

    if not valores:
        return jsonify({"error": "No se enviaron campos para actualizar."}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Validar si el usuario existe
            cur.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
            if not cur.fetchone():
                return jsonify({"error": "Usuario no encontrado."}), 404

            # Validar correo duplicado (si se va a actualizar)
            if 'correo' in valores:
                cur.execute("SELECT id FROM usuarios WHERE correo = %s AND id <> %s", (valores['correo'], id))
                if cur.fetchone():
                    return jsonify({"error": "Ya existe otro usuario con ese correo."}), 409

            # Preparar campos para la consulta UPDATE
            sets = []
            parametros = []

            for campo, valor in valores.items():
                if campo == 'contrasena':
                    valor = generate_password_hash(valor)
                sets.append(f"{campo} = %s")
                parametros.append(valor)

            parametros.append(id)

            cur.execute(f"""
                UPDATE usuarios
                SET {', '.join(sets)}
                WHERE id = %s
            """, parametros)

            conn.commit()

        return jsonify({"mensaje": "Usuario actualizado correctamente."}), 200

    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

@usuarios_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Verificar si el usuario existe
            cur.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
            if not cur.fetchone():
                return jsonify({"error": "Usuario no encontrado."}), 404

            # Eliminar usuario
            cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
            conn.commit()

        return jsonify({"mensaje": "Usuario eliminado correctamente."}), 200

    except Exception as e:
        return jsonify({"error": f"Error al eliminar usuario: {str(e)}"}), 500

    
    
@usuarios_bp.route('/listar', methods=['GET'])
def vista_lista_usuarios():
    return render_template('usuarios/index.html')



