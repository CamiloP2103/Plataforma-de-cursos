from flask import Flask, request, session, redirect, render_template, url_for
from config import Config
from functools import wraps
from models import db
from auth_service import AuthService

app = Flask(__name__, template_folder='html', static_folder='css')
app.config.from_object(Config)
db.init_app(app)
# Usuarios en memoria (usar solo como respaldo si la BD falla)
USUARIOS_BACKUP = {
    'admin': {'password': '1234', 'rol': 'admin'},
    'usuario1': {'password': 'password1', 'rol': 'estudiante'},
    'profesor1': {'password': 'prof123', 'rol': 'profesor'}
}

# Función decoradora para verificar roles
def rol_requerido(roles_permitidos):
    def decorator(funcion):
        @wraps(funcion)
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

@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        nombre = request.form.get('nombre')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            return render_template("sign-up.html", error="Las contraseñas no coinciden")
        if AuthService.register(nombre, password):
            return redirect('/')
        else:
            return render_template("sign-up.html", error="Hubo un error al registrar el usuario.")
    return render_template("sign-up.html")

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    rol = AuthService.login(username, password)
    if rol:
        if rol == 'profesor':
            return redirect('/profesor/dashboard')
        elif rol == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect('/home')
    if username in USUARIOS_BACKUP and USUARIOS_BACKUP[username]['password'] == password:
        session['usuario'] = username
        session['rol'] = USUARIOS_BACKUP[username]['rol']
        if USUARIOS_BACKUP[username]['rol'] == 'profesor':
            return redirect('/profesor/dashboard')
        elif USUARIOS_BACKUP[username]['rol'] == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect('/home')
    return render_template('acceso_denegado.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('rol', None)
    return redirect('/')

@app.route('/home')
@rol_requerido(['estudiante', 'admin'])

def homepage():
    return render_template('home.html', usuario=session['usuario'])
    print(session.pop('rol', None))
@app.route('/profesor/dashboard')
@rol_requerido(['profesor', 'admin'])
def profesor_dashboard():
    return render_template('profesor_dashboard.html', usuario=session['usuario'])

@app.route('/admin/dashboard')
@rol_requerido(['admin'])
def admin_dashboard():
    return render_template('admin_dashboard.html', usuario=session['usuario'])
    
# Nueva ruta para que los profesores puedan crear cursos
@app.route('/profesor/crear_curso', methods=['GET', 'POST'])
@rol_requerido(['profesor'])
def crear_curso():
    if request.method == 'POST':
        nombre_curso = request.form.get('nombre_curso')
        descripcion = request.form.get('descripcion')
        nuevo_curso = Cursos(nombre_curso=nombre_curso, descripcion=descripcion)
        db.session.add(nuevo_curso)
        db.session.commit()
        return redirect('/profesor/dashboard')
    return render_template('crear_curso.html')
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
