import unittest
from app import app, db
from models import Usuarios, Cursos, ArchivosCurso
from sqlalchemy.exc import IntegrityError
from config import Config

class TestDatabaseConstraints(unittest.TestCase):
    """Pruebas para las restricciones de la base de datos"""

    @classmethod
    def setUpClass(cls):
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
        app.config['TESTING'] = True
        cls.app_context = app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def setUp(self):
        self.profesor = Usuarios(
            Nombre="profesor_constraints",
            Contraseña="hash_prof",
            Tipo_usr=1,
            estado=True
        )
        db.session.add(self.profesor)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        ArchivosCurso.query.delete()
        Cursos.query.delete()
        Usuarios.query.delete()
        db.session.commit()

    def test_foreign_key_profesor(self):
        """Prueba que no se puede crear curso con profesor_id inválido"""
        with self.assertRaises(IntegrityError):
            curso = Cursos(
                nombre_curso="Curso Inválido",
                profesor_id=9999  # ID que no existe
            )
            db.session.add(curso)
            db.session.commit()

    def test_cascade_delete_archivos(self):
        """Prueba que los archivos se eliminan al borrar el curso"""
        curso = Cursos(
            nombre_curso="Temporal",
            profesor_id=self.profesor.id_usr
        )
        archivo = ArchivosCurso(
            nombre_archivo="temp.pdf",
            ruta_archivo="uploads/temp.pdf",
            curso=curso
        )
        db.session.add_all([curso, archivo])
        db.session.commit()
        
        # Eliminar curso
        db.session.delete(curso)
        db.session.commit()
        
        # Verificar que el archivo también se eliminó
        archivo_db = ArchivosCurso.query.get(archivo.id)
        self.assertIsNone(archivo_db)

    def test_null_constraints(self):
        """Prueba que los campos requeridos no pueden ser NULL"""
        with self.assertRaises(IntegrityError):
            usuario = Usuarios(
                Nombre=None,  # Campo requerido
                Contraseña="hash"
            )
            db.session.add(usuario)
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
