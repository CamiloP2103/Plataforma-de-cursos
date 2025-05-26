import unittest
from app import app
from models import db, Usuarios, Cursos, ArchivosCurso

class TestModels(unittest.TestCase):
    """Pruebas para los modelos de la base de datos"""
    
    def setUp(self):
        """
        Configuración inicial antes de cada prueba:
        - Crea una base de datos en memoria
        - Establece contexto de aplicación
        """
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app_context = app.app_context()  # Contexto para acceder a Flask
        self.app_context.push()  # Activar contexto
        db.create_all()  # Crear tablas
    
    def tearDown(self):
        """
        Limpieza después de cada prueba:
        - Elimina la base de datos
        - Remueve el contexto
        """
        db.session.remove()  # Limpiar sesión
        db.drop_all()  # Eliminar tablas
        self.app_context.pop()  # Desactivar contexto
    
    def test_usuario_curso_relationship(self):
        """
        Prueba la relación muchos-a-muchos entre usuarios y cursos:
        - Un usuario puede estar inscrito en muchos cursos
        - Un curso puede tener muchos estudiantes
        """
        # Crear datos de prueba
        usuario = Usuarios(Nombre="estudiante1", Contraseña="pass", Tipo_usr=2)
        curso = Cursos(nombre_curso="Matemáticas", descripcion="Curso básico")
        
        # Establecer relación (usuario inscrito en curso)
        usuario.cursos_inscritos.append(curso)
        
        # Guardar en la base de datos
        db.session.add_all([usuario, curso])
        db.session.commit()
        
        # Verificar relaciones:
        # - El usuario debe tener 1 curso inscrito
        self.assertEqual(len(usuario.cursos_inscritos), 1)
        # - El curso debe tener 1 estudiante
        self.assertEqual(len(curso.estudiantes), 1)
        # - Verificar nombres
        self.assertEqual(usuario.cursos_inscritos[0].nombre_curso, "Matemáticas")
        self.assertEqual(curso.estudiantes[0].Nombre, "estudiante1")
    
    def test_curso_archivo_relationship(self):
        """
        Prueba la relación uno-a-muchos entre cursos y archivos:
        - Un curso puede tener muchos archivos
        - Cada archivo pertenece a un solo curso
        """
        # Crear datos
        curso = Cursos(nombre_curso="Programación")
        archivo = ArchivosCurso(
            nombre_archivo="intro.pdf",
            ruta_archivo="uploads/intro.pdf",
            curso=curso  # Establecer relación
        )
        
        # Guardar
        db.session.add_all([curso, archivo])
        db.session.commit()
        
        # Verificar:
        # - El curso debe tener 1 archivo
        self.assertEqual(len(curso.archivos), 1)
        # - El archivo debe estar asociado al curso correcto
        self.assertEqual(archivo.curso.nombre_curso, "Programación")
    
    def test_usuario_creation_defaults(self):
        """
        Prueba los valores por defecto al crear un usuario:
        - Tipo_usr debe ser 2 (estudiante) por defecto
        - Estado debe ser True (activo) por defecto
        """
        # Crear usuario sin especificar tipo o estado
        usuario = Usuarios(Nombre="test", Contraseña="pass")
        db.session.add(usuario)
        db.session.commit()
        
        # Verificar valores por defecto
        self.assertEqual(usuario.Tipo_usr, 2)  # 2 = estudiante
        self.assertTrue(usuario.Estado)  # Debe estar activo

if __name__ == '__main__':
    unittest.main()
