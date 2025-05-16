
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuarios(db.Model):
    __tablename__ = 'USUARIOS'
    id_usr = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(256))
    Contraseña = db.Column(db.String(256))
    Tipo_usr = db.Column(db.Integer)
    Estado = db.Column(db.Boolean, default=True)
    
class Cursos(db.Model):
    __tablename__ = 'CURSOS'
    id_curso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_curso = db.Column(db.String(256))
    descripcion = db.Column(db.String(512))
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    
