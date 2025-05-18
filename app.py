from flask import Flask, request, session, redirect, render_template, url_for
from config import Config
from functools import wraps
from models import db, Cursos, Usuarios
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
    usuario = Usuarios.query.filter_by(Nombre=session['usuario']).first()
    cursos = usuario.cursos_inscritos if usuario else []
    return render_template('home.html', usuario=usuario.Nombre, cursos=cursos)
    

@app.route('/cursos')
@rol_requerido(['estudiante'])
def ver_cursos():
    usuario = Usuarios.query.filter_by(Nombre=session['usuario']).first()
    cursos_disponibles = Cursos.query.filter(~Cursos.estudiantes.any(id_usr=usuario.id_usr)).all()
    return render_template('cursos_disponibles.html', cursos=cursos_disponibles, usuario=usuario.Nombre)

@app.route('/inscribirse/<int:curso_id>')
@rol_requerido(['estudiante'])
def inscribirse(curso_id):
    usuario = Usuarios.query.filter_by(Nombre=session['usuario']).first()
    curso = Cursos.query.get(curso_id)

    if curso and usuario not in curso.estudiantes:
        usuario.cursos_inscritos.append(curso)
        db.session.commit()
    
    return redirect('/home')
    

@app.route('/profesor/dashboard')
@rol_requerido(['profesor', 'admin'])
def profesor_dashboard():
    profesor = Usuarios.query.filter_by(Nombre=session['usuario']).first()
    cursos = Cursos.query.filter_by(profesor_id=profesor.id_usr).all() if profesor else []
    return render_template('profesor_dashboard.html', usuario=profesor.Nombre, cursos=cursos)

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

        # Obtener el usuario actual (profesor)
        profesor = Usuarios.query.filter_by(Nombre=session['usuario']).first()

        if not profesor:
            return render_template("crear_curso.html", error="No se encontró al profesor.")

        # Crear y asociar el curso
        nuevo_curso = Cursos(
            nombre_curso=nombre_curso,
            descripcion=descripcion,
            profesor_id=profesor.id_usr
        )
        db.session.add(nuevo_curso)
        db.session.commit()

        return redirect('/profesor/dashboard')

    return render_template('crear_curso.html')

    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
