
from models import Usuarios, db
from flask import session, redirect, render_template
import bcrypt

TIPO_USUARIO_A_ROL = {
    1: 'profesor',
    2: 'estudiante',
    3: 'admin'
}

class AuthService:
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def check_password(password, hashed_password):
        # Asegurarse de que el hash esté en formato bytes
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    @staticmethod
    def login(username, password):
        try:
            usuario = Usuarios.query.filter_by(Nombre=username).first()
            if usuario and AuthService.check_password(password, usuario.Contraseña):
                tipo_usuario = usuario.Tipo_usr
                rol = TIPO_USUARIO_A_ROL.get(tipo_usuario, 'estudiante')
                session['usuario'] = usuario.Nombre
                session['rol'] = rol
                return rol
        except Exception as e:
            print(f"Error en login: {e}")
        return None

    @staticmethod
    def register(nombre, password, tipo_usr=2):
        try:
            hashed_password = AuthService.hash_password(password)
            nuevo_usuario = Usuarios(
                Nombre=nombre,
                Contraseña=hashed_password.decode('utf-8'),  # Guardar como string
                Tipo_usr=tipo_usr,
                Estado=True
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el usuario: {e}")
            return False


