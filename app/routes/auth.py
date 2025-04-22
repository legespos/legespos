from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash
from app.db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')

        if not correo or not contrasena:
            return render_template('auth/login.html', error='Todos los campos son obligatorios.')

        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT id, nombre, contrasena FROM usuarios WHERE correo = %s AND activo = TRUE", (correo,))
                user = cur.fetchone()

                if user and check_password_hash(user[2], contrasena):
                    # Aquí podrías usar sesión
                    return redirect(url_for('usuarios.vista_lista_usuarios'))
                else:
                    return render_template('auth/login.html', error='Credenciales incorrectas.')

        except Exception as e:
            return render_template('auth/login.html', error=f'Error del servidor: {str(e)}')

    return render_template('auth/login.html')
