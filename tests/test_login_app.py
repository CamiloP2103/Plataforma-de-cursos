import unittest
from app import app

class FlaskLoginTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_login_successful_backup_user(self):
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': '1234'
        }, follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)

    def test_login_failure(self):
        response = self.client.post('/login', data={
            'username': 'invalido',
            'password': 'mal'
        })
        self.assertIn(b'Acceso denegado', response.data)

    def test_signup_password_mismatch(self):
        response = self.client.post('/sign-up', data={
            'nombre': 'usuario_test',
            'fecha_nacimiento': '2000-01-01',
            'password': 'abc123',
            'confirm_password': 'abc321'
        })
        self.assertIn(b'Las contrase', response.data)

if __name__ == '__main__':
    unittest.main()
