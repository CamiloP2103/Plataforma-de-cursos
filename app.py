from flask import Flask, request, session, redirect, render_template, url_for
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, template_folder='html', static_folder='css')
app.secret_key = 'clave_secreta'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://UserPlataforma:Ucatolica1@3.145.105.164:3306/plataformacursos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definición del modelo según la estructura de la tabla USUARIOS
class Usuarios(db.Model):
    __tablename__ = 'USUARIOS'
    id_usr = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(256))
    Contraseña = db.Column(db.String(256))
    Tipo_usr = db.Column(db.Integer)

# Usuarios en memoria (usar solo como respaldo si la BD falla)
USUARIOS_BACKUP = {
    'admin': {'password': '1234', 'rol': 'admin'},
    'usuario1': {'password': 'password1', 'rol': 'estudiante'},
    'profesor1': {'password': 'prof123', 'rol': 'profesor'}
}

# Mapa para convertir tipo de usuario a rol
TIPO_USUARIO_A_ROL = {
    1: 'profesor',
    2: 'estudiante',
    3: 'admin'
    # Puedes agregar más tipos si es necesario
}

# Función decoradora para verificar roles
def rol_requerido(roles_permitidos):
    def decorator(funcion):
        @wraps(funcion)  # Esto preserva el nombre y los metadatos de la función
        def wrapper(*args, **kwargs):
            if 'usuario' not in session:
                return redirect('/')
            
            if session['rol'] not in roles_permitidos:
                return render_template('acceso_denegado.html')
            
            return funcion(*args, **kwargs)
        return wrapper
    return decorator

# Encuentra el index principal al iniciar la pagina
@app.route('/')
def home():
    return render_template('index.html')

# Toma las credenciales que se le estan pidiendo al usuario en el index
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    try:
        # Buscar en la tabla USUARIOS
        usuario = Usuarios.query.filter_by(Nombre=username, Contraseña=password).first()
        
        if usuario:
            # Obtener rol basado en el tipo de usuario
            tipo_usuario = usuario.Tipo_usr
            rol = TIPO_USUARIO_A_ROL.get(tipo_usuario, 'estudiante')  # Por defecto estudiante
            
            session['usuario'] = usuario.Nombre
            session['rol'] = rol
            
            # Redirigir según el rol
            if rol == 'profesor':
                return redirect('/profesor/dashboard')
            elif rol == 'admin':
                return redirect('/admin/dashboard')
            else:
                return redirect('/home')
        
        # Si no encuentra en la BD, usar el respaldo en memoria (solo para desarrollo)
        if username in USUARIOS_BACKUP and USUARIOS_BACKUP[username]['password'] == password:
            session['usuario'] = username
            session['rol'] = USUARIOS_BACKUP[username]['rol']
            
            # Redirigir según el rol
            if USUARIOS_BACKUP[username]['rol'] == 'profesor':
                return redirect('/profesor/dashboard')
            elif USUARIOS_BACKUP[username]['rol'] == 'admin':
                return redirect('/admin/dashboard')
            else:
                return redirect('/home')
    except Exception as e:
        print(f"Error en login: {e}")
        # Si hay error en la BD, usar el respaldo en memoria
        if username in USUARIOS_BACKUP and USUARIOS_BACKUP[username]['password'] == password:
            session['usuario'] = username
            session['rol'] = USUARIOS_BACKUP[username]['rol']
            
            # Redirigir según el rol
            if USUARIOS_BACKUP[username]['rol'] == 'profesor':
                return redirect('/profesor/dashboard')
            elif USUARIOS_BACKUP[username]['rol'] == 'admin':
                return redirect('/admin/dashboard')
            else:
                return redirect('/home')
    
    return render_template('acceso_denegado.html')

# Función para cerrar sesion y volver al index.html
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('rol', None)
    return redirect('/')

# Ruta para estudiantes (la actual home.html)
@app.route('/home')
@rol_requerido(['estudiante', 'admin'])
def homepage():
    return render_template('home.html', usuario=session['usuario'])

# Ruta para profesores
@app.route('/profesor/dashboard')
@rol_requerido(['profesor', 'admin'])
def profesor_dashboard():
    return render_template('profesor_dashboard.html', usuario=session['usuario'])

# Ruta para administradores
@app.route('/admin/dashboard')
@rol_requerido(['admin'])
def admin_dashboard():
    return render_template('admin_dashboard.html', usuario=session['usuario'])

if __name__ == '__main__':
    # Crear la tabla si no existe
    with app.app_context():
        db.create_all()
    app.run(debug=True)