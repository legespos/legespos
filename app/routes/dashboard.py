from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/home')
def home():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template(
        'dashboard/home.html',
        nombre=session.get('usuario_nombre'),
        rol=session.get('usuario_rol')
    )
