import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
from sqlalchemy import text  # Importa la función text

class TestDBConnection(unittest.TestCase):
    """
    Clase de prueba para verificar la conexión a la base de datos.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas. Se ejecuta antes de cada método de prueba.
        """
        # Crea una instancia de la aplicación Flask para las pruebas
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://UserPlataforma:Hola12@DESKTOP-57PO3BN/plataformacursos'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = SQLAlchemy(self.app)
        self.app.app_context().push()  # Empuja un contexto de aplicación para poder usar self.db


    def test_conexion_exitosa(self):
        """
        Prueba que la conexión a la base de datos se establece correctamente.
        """
        
        
        try:
            # Intenta ejecutar una consulta simple para verificar la conexión
            result = self.db.session.execute(text("SELECT * from plataformacursos.usuarios")).fetchone()  # Usa text()
            conexion_exitosa = True
            print("Prueba que la conexion a la base de datos se establece correctamente." )
            print(result)  # Imprime el resultado
        except pymysql.OperationalError:
            conexion_exitosa = False
        except Exception as e:
            print(f"Error inesperado: {e}")  # Imprime cualquier otro error
            conexion_exitosa = False
        self.assertTrue(conexion_exitosa, "No se pudo conectar a la base de datos, Valide password")

    def test_conexion_fallida_credenciales_incorrectas(self):
        """
        Prueba que la conexión falla con credenciales incorrectas.
        """
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://UserPlataforma:Hola1@DESKTOP-57PO3BN/plataformacursos'  #Credenciales incorrectas
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        app.app_context().push()

        conexion_fallida = False
        try:
            db.session.execute(text("SELECT 1")).fetchone() # Usa text()
        except pymysql.OperationalError as e:
            if "Access denied" in str(e): #Verifica el mensaje de error esperado
                conexion_fallida = True
        except Exception as e:
            print(f"Error inesperado: {e}")
            conexion_fallida = False

        self.assertTrue(conexion_fallida, "La conexión no falló con credenciales incorrectas")

if __name__ == '__main__':
    unittest.main()
