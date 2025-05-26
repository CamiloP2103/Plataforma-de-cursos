from flask import Flask, request, session, redirect, render_template, url_for, flash
from config import Config
from functools import wraps
from models import db, Cursos, Usuarios,ArchivosCurso 
from auth_service import AuthService
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from podcast_service import generar_podcast_desde_pdf
import random
import os

app = Flask(__name__, template_folder='html', static_folder='static')

app.config.from_object(Config)
db.init_app(app)

# Carpeta para guardar los archivos PDF
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE_MB = 25
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024  # 5 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
@app.route('/')
def home():
    todos_cursos = obtener_todos_los_cursos()
    cursos_muestra = random.sample(todos_cursos, min(3, len(todos_cursos))) if todos_cursos else []
    return render_template('index.html', cursos=cursos_muestra)

def obtener_todos_los_cursos():
    return Cursos.query.all()  # Trae todos los cursos de la tabla

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
    cursos_disponibles = Cursos.query.count()
    cursos_en_progreso = len(cursos)
    cursos_completados = 0  
    return render_template(
        'home.html',
        usuario=usuario.Nombre,
        cursos=cursos,
        cursos_disponibles=cursos_disponibles,
        cursos_en_progreso=cursos_en_progreso,
        cursos_completados=cursos_completados
    )

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

@app.route('/generar_podcast/<int:id>', methods=['GET', 'POST'])
@rol_requerido(['estudiante'])
def generar_podcast(id):
    archivo = ArchivosCurso.query.get_or_404(id)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], archivo.ruta_archivo)

    if not os.path.exists(pdf_path):
        flash("El archivo no existe.")
        return redirect(request.referrer or '/home')
    
        # Si ya tiene podcast generado, lo usamos directamente (no se regenera)
    if archivo.ruta_podcast:
        mensaje_info = "✅ Este podcast ya fue generado anteriormente."
        return render_template(
        'podcast_generado.html',
        audio_url='/' + archivo.ruta_podcast,
        archivo=archivo,
        transcripcion=archivo.transcripcion,
        mensaje_info=mensaje_info
    )


    if request.method == 'POST':
        pregunta = request.form.get("pregunta", "")
        idioma = request.form.get("idioma", "")
        resultado = generar_podcast_desde_pdf(pdf_path, pregunta=pregunta, idioma=idioma)

      
    if isinstance(resultado, tuple) and "static/podcasts/" in resultado[0].replace("\\", "/"):
        ruta_podcast, transcripcion = resultado

          
        # ✅ GUARDAR EN BASE DE DATOS MY SQL DESPLEIGUE AUTOMATICO EN LA PRESENTACION
        ruta_podcast = resultado[0].replace("\\", "/")
        archivo.ruta_podcast = ruta_podcast
        archivo.transcripcion = transcripcion
        db.session.commit()

        return render_template('podcast_generado.html', audio_url='/' + ruta_podcast, archivo=archivo, transcripcion=transcripcion)

    else:
        flash(f"Error al generar el podcast: {resultado}")
        return redirect(request.referrer or '/home')


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
    
# Metodo Editar curso por profesor

@app.route('/profesor/editar_curso/<int:curso_id>', methods=['GET', 'POST'])
@rol_requerido(['profesor'])
def editar_curso(curso_id):
    curso = Cursos.query.get_or_404(curso_id)
    profesor = Usuarios.query.filter_by(Nombre=session['usuario']).first()

    if curso.profesor_id != profesor.id_usr:
        return render_template('acceso_denegado.html')

    if request.method == 'POST':
        curso.nombre_curso = request.form.get('nombre_curso')
        curso.descripcion = request.form.get('descripcion')

        archivos = request.files.getlist('pdfs')
        for archivo in archivos:
            if archivo and archivo.filename.endswith('.pdf'):
                filename = secure_filename(archivo.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                archivo.save(filepath)

                nuevo_archivo = ArchivosCurso(
                    nombre_archivo=filename,
                    ruta_archivo=filename,
                    curso_id=curso.id_curso
                )
                db.session.add(nuevo_archivo)
        
        db.session.commit()
        return redirect('/profesor/dashboard')

    return render_template('editar_curso.html', curso=curso)

 #valida el tamaño de archivo y que sea pdf 
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("El archivo excede el tamaño máximo permitido de 25 MB.")
    # Puedes usar request.referrer para volver a la misma página
    return redirect(request.referrer or '/')

    
#Eliminar cursos profesor 

@app.route('/profesor/eliminar_curso/<int:curso_id>', methods=['POST'])
@rol_requerido(['profesor'])
def eliminar_curso(curso_id):
    curso = Cursos.query.get_or_404(curso_id)
    profesor = Usuarios.query.filter_by(Nombre=session['usuario']).first()

    if curso.profesor_id != profesor.id_usr:
        return render_template('acceso_denegado.html')

    db.session.delete(curso)
    db.session.commit()
    return redirect('/profesor/dashboard')
    
# consultar contenido curso 

@app.route('/curso/<int:curso_id>')
@rol_requerido(['estudiante'])
def ver_curso(curso_id):
    usuario = Usuarios.query.filter_by(Nombre=session['usuario']).first()
    curso = Cursos.query.get_or_404(curso_id)

    # Validar que el estudiante esté inscrito en el curso
    if usuario not in curso.estudiantes:
        return render_template('acceso_denegado.html')

    return render_template('curso_estudiante.html', usuario=usuario.Nombre, curso=curso)    

