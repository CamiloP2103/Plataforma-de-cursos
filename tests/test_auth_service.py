import unittest
from unittest.mock import patch, MagicMock
from auth_service import AuthService
from models import Usuarios

class TestAuthService(unittest.TestCase):
    """Pruebas para el servicio de autenticación (auth_service.py)"""
    
    @patch('auth_service.db')  # Mock de la base de datos
    def test_register_success(self, mock_db):
        """
        Prueba que el registro de usuario funciona correctamente
        cuando se proporcionan credenciales válidas
        """
        # Configurar mocks
        mock_db.session.add.return_value = None  # Simula éxito al añadir usuario
        mock_db.session.commit.return_value = None  # Simula éxito al guardar
        
        # Mock del hash de contraseña
        with patch('auth_service.bcrypt.hashpw') as mock_hash:
            mock_hash.return_value = b'hashed_password'  # Simula contraseña hasheada
            
            # Ejecutar el método a probar
            result = AuthService.register("nuevo_usuario", "password123")
            
            # Verificar que retorna True (éxito)
            self.assertTrue(result)
            # Verificar que se llamó a guardar el usuario
            mock_db.session.add.assert_called_once()
    
    @patch('auth_service.db')
    def test_register_failure(self, mock_db):
        """
        Prueba que el registro falla adecuadamente cuando hay
        un error en la base de datos
        """
        # Simular error al añadir usuario
        mock_db.session.add.side_effect = Exception("DB Error")
        
        # Ejecutar registro (debería fallar)
        result = AuthService.register("nuevo_usuario", "password123")
        
        # Verificar que retorna False (fallo)
        self.assertFalse(result)
    
    @patch('auth_service.db')
    def test_check_password(self, mock_db):
        """
        Prueba que la verificación de contraseña compara correctamente
        la contraseña ingresada con el hash almacenado
        """
        # Configurar usuario simulado
        mock_user = MagicMock()
        mock_user.Contraseña = b'hashed_password'  # Contraseña "almacenada"
        
        # Configurar mock para retornar el usuario simulado
        mock_db.session.query().filter_by().first.return_value = mock_user
        
        # Mock de la verificación de bcrypt
        with patch('auth_service.bcrypt.checkpw', return_value=True):
            # Verificar contraseña correcta
            is_valid = AuthService.check_password("input_pass", "hashed_password")
            self.assertTrue(is_valid)

if __name__ == '__main__':
    unittest.main()  # Permite ejecutar las pruebas con: python test_auth_service.py
