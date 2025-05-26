import unittest
import os
import tempfile
from unittest.mock import patch
from podcast_service import generar_podcast_desde_pdf

class TestPodcastService(unittest.TestCase):
    
    @patch('podcast_service.Client')
    @patch('podcast_service.shutil.copy')
    def test_generate_podcast_success(self, mock_copy, mock_client):
        """Prueba generación exitosa de podcast"""
        # Configurar mocks
        mock_instance = mock_client.return_value
        mock_instance.predict.return_value = ("temp.mp3", "transcripción")
        mock_copy.return_value = None
        
        # Crear archivo PDF temporal
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'PDF content')
            tmp_path = tmp.name
        
        try:
            result = generar_podcast_desde_pdf(tmp_path)
            self.assertEqual(len(result), 2)  # Debe retornar (ruta, transcripción)
            self.assertIn('static/podcasts', result[0])
        finally:
            os.unlink(tmp_path)
    
    @patch('podcast_service.Client')
    def test_generate_podcast_file_not_found(self, mock_client):
        """Prueba manejo de archivo no encontrado"""
        with self.assertRaises(Exception):
            generar_podcast_desde_pdf("nonexistent.pdf")
    
    @patch('podcast_service.Client')
    def test_generate_podcast_api_error(self, mock_client):
        """Prueba manejo de error en API externa"""
        mock_client.return_value.predict.side_effect = Exception("API Error")
        result = generar_podcast_desde_pdf("dummy.pdf")
        self.assertIn("Error al generar podcast", result)

if __name__ == '__main__':
    unittest.main()
