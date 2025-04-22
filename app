from flask import Flask, request, session, redirect, render_template, url_for
from functools import wraps

app = Flask(__name__, template_folder='html', static_folder='css')
app.secret_key = 'clave_secreta'

# Usuarios con roles
USUARIOS = {
    'admin': {'password': '1234', 'rol': 'admin'},
    'usuario1': {'password': 'password1', 'rol': 'estudiante'},
    'profesor1': {'password': 'prof123', 'rol': 'profesor'}
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
    
    if username in USUARIOS and USUARIOS[username]['password'] == password:
        session['usuario'] = username
        session['rol'] = USUARIOS[username]['rol']
        
        # Redirigir según el rol
        if USUARIOS[username]['rol'] == 'profesor':
            return redirect('/profesor/dashboard')
        elif USUARIOS[username]['rol'] == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect('/home')
    
    error = "Usuario o contraseña inválida. Intente de nuevo."
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

# Ruta para administradores (opcional)
@app.route('/admin/dashboard')
@rol_requerido(['admin'])
def admin_dashboard():
    # Puedes crear una plantilla admin_dashboard.html similar a profesor_dashboard.html
    return render_template('admin_dashboard.html', usuario=session['usuario'])

if __name__ == '__main__':
    app.run(debug=True)