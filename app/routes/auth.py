from flask import Blueprint, render_template, request, redirect, url_for, session
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
                cur.execute("""
                    SELECT u.id, u.nombre, u.contrasena, r.nombre AS rol
                    FROM usuarios u
                    JOIN roles r ON u.rol_id = r.id
                    WHERE u.correo = %s AND u.activo = TRUE
                """, (correo,))
                user = cur.fetchone()

                if user and check_password_hash(user[2], contrasena):
                    session['usuario_id'] = user[0]
                    session['usuario_nombre'] = user[1]
                    session['usuario_rol'] = user[3]
                    return redirect(url_for('dashboard.home'))

            # Si no autenticó dentro del with
            return render_template('auth/login.html', error='Credenciales inválidas.')

        except Exception as e:
            return render_template('auth/login.html', error=f'Error del servidor: {str(e)}')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

