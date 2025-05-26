import unittest
from app import app, db
from models import Usuarios, Cursos, ArchivosCurso
import mysql.connector
from config import Config

class TestDatabaseModels(unittest.TestCase):
    """Pruebas para los modelos de base de datos"""

    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todas las pruebas"""
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
        app.config['TESTING'] = True
        cls.app_context = app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        """Limpieza final"""
        cls.app_context.pop()

    def setUp(self):
        """Preparar datos para cada prueba"""
        # Crear un profesor
        self.profesor = Usuarios(
            Nombre="profesor_test",
            Contraseña="hash_prof",
            Tipo_usr=1,  # 1 = profesor
            estado=True
        )
        db.session.add(self.profesor)
        db.session.commit()

    def tearDown(self):
        """Limpiar datos después de cada prueba"""
        db.session.rollback()
        # Limpiar tablas en orden correcto por restricciones FK
        ArchivosCurso.query.delete()
        Cursos.query.delete()
        Usuarios.query.delete()
        db.session.commit()

    def test_usuario_creation(self):
        """Prueba creación de usuario con valores por defecto"""
        estudiante = Usuarios(
            Nombre="estudiante_test",
            Contraseña="hash_est"
        )
        db.session.add(estudiante)
        db.session.commit()
        
        # Verificar valores por defecto
        self.assertEqual(estudiante.Tipo_usr, 2)  # 2 = estudiante por defecto
        self.assertTrue(estudiante.estado)  # True por defecto

    def test_curso_creation(self):
        """Prueba creación de curso con profesor"""
        curso = Cursos(
            nombre_curso="Matemáticas",
            descripcion="Curso básico de matemáticas",
            profesor_id=self.profesor.id_usr
        )
        db.session.add(curso)
        db.session.commit()
        
        # Verificar relaciones
        self.assertEqual(curso.profesor_id, self.profesor.id_usr)
        self.assertIn(curso, self.profesor.cursos_impartidos)

    def test_archivo_curso_relationship(self):
        """Prueba relación entre cursos y archivos"""
        curso = Cursos(
            nombre_curso="Programación",
            profesor_id=self.profesor.id_usr
        )
        archivo = ArchivosCurso(
            nombre_archivo="intro.pdf",
            ruta_archivo="uploads/intro.pdf",
            curso=curso
        )
        db.session.add_all([curso, archivo])
        db.session.commit()
        
        # Verificar relaciones
        self.assertEqual(archivo.curso_id, curso.id_curso)
        self.assertEqual(len(curso.archivos), 1)
        self.assertEqual(curso.archivos[0].nombre_archivo, "intro.pdf")

    def test_curso_estudiante_relationship(self):
        """Prueba relación muchos-a-muchos entre estudiantes y cursos"""
        estudiante = Usuarios(
            Nombre="estudiante_rel",
            Contraseña="hash_est",
            Tipo_usr=2
        )
        curso = Cursos(
            nombre_curso="Física",
            profesor_id=self.profesor.id_usr
        )
        
        # Establecer relación
        estudiante.cursos_inscritos.append(curso)
        db.session.add_all([estudiante, curso])
        db.session.commit()
        
        # Verificar relaciones
        self.assertEqual(len(estudiante.cursos_inscritos), 1)
        self.assertEqual(len(curso.estudiantes), 1)
        self.assertEqual(curso.estudiantes[0].Nombre, "estudiante_rel")

if __name__ == '__main__':
    unittest.main()
