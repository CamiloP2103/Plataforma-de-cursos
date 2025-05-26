
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Relación muchos-a-muchos entre estudiantes y cursos
curso_estudiante = db.Table('CURSO_ESTUDIANTE',
    db.Column('usuario_id', db.Integer, db.ForeignKey('USUARIOS.id_usr')),
    db.Column('curso_id', db.Integer, db.ForeignKey('CURSOS.id_curso'))
)    

class Usuarios(db.Model):
    __tablename__ = 'USUARIOS'
    id_usr = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(256))
    Contraseña = db.Column(db.String(256))
    Tipo_usr = db.Column(db.Integer)
    Estado = db.Column(db.Boolean, default=True)
    # se agrega campo de fecha 
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    # Relación con cursos inscritos (para estudiantes)
    cursos_inscritos = db.relationship('Cursos', secondary=curso_estudiante, backref='estudiantes')
    
class Cursos(db.Model):
    __tablename__ = 'CURSOS'
    id_curso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_curso = db.Column(db.String(256))
    descripcion = db.Column(db.String(512))
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    profesor_id = db.Column(db.Integer, db.ForeignKey('USUARIOS.id_usr'))
    profesor = db.relationship('Usuarios', backref='cursos_impartidos')

class ArchivosCurso(db.Model):
    __tablename__ = 'ARCHIVOS_CURSO'
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(256))
    ruta_archivo = db.Column(db.String(512))
    ruta_podcast = db.Column(db.String(512))
    transcripcion = db.Column(db.Text)  # NUEVO
    curso_id = db.Column(db.Integer, db.ForeignKey('CURSOS.id_curso'))
    curso = db.relationship('Cursos', backref='archivos')

