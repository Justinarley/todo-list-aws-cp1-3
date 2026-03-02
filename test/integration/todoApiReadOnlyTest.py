import os
import unittest
import requests
import pytest

BASE_URL = os.environ.get("BASE_URL")
DEFAULT_TIMEOUT = 30  # in secs (aumentado para cold starts de Lambda)


@pytest.mark.readonly
class TestApiReadOnly(unittest.TestCase):
    """
    Pruebas de solo lectura para ambiente de producción.
    No crea, modifica ni elimina datos.
    """
    
    def setUp(self):
        self.assertIsNotNone(BASE_URL, "URL no configurada")
        self.assertTrue(len(BASE_URL) > 8, "URL no configurada")

    def test_api_health_check(self):
        """Verifica que la API responde correctamente"""
        print('---------------------------------------')
        print('Starting - Health Check')
        url = BASE_URL + "/todos"
        print(f'URL: {url}')
        
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        
        print(f'Response Status: {response.status_code}')
        print(f'Response Body: {response.json()}')
        
        self.assertEqual(
            response.status_code, 200, 
            f"Error en la petición API a {url}"
        )
        
        # Verifica que devuelve una lista (puede estar vacía)
        json_response = response.json()
        self.assertIsInstance(
            json_response, list,
            "La respuesta debe ser una lista"
        )
        
        print('End - Health Check')
        print('---------------------------------------')

    def test_api_list_todos_structure(self):
        """Verifica la estructura de la respuesta de list todos"""
        print('---------------------------------------')
        print('Starting - List TODOs Structure Test')
        url = BASE_URL + "/todos"
        print(f'URL: {url}')
        
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        
        self.assertEqual(
            response.status_code, 200,
            f"Error en la petición API a {url}"
        )
        
        json_response = response.json()
        print(f'Number of todos: {len(json_response)}')
        
        # Si hay TODOs, verifica la estructura del primero
        if len(json_response) > 0:
            first_todo = json_response[0]
            print(f'First TODO: {first_todo}')
            
            # Verifica que tenga los campos esperados
            self.assertIn('id', first_todo, "TODO debe tener campo 'id'")
            self.assertIn('text', first_todo, "TODO debe tener campo 'text'")
            
            # Verifica tipos de datos
            self.assertIsInstance(first_todo['id'], str, "id debe ser string")
            self.assertIsInstance(first_todo['text'], str, "text debe ser string")
            
            print(f"TODO structure validated successfully")
        else:
            print("No TODOs found (empty list is valid)")
        
        print('End - List TODOs Structure Test')
        print('---------------------------------------')

    def test_api_response_time(self):
        """Verifica que la API responde en tiempo razonable"""
        print('---------------------------------------')
        print('Starting - Response Time Test')
        url = BASE_URL + "/todos"
        print(f'URL: {url}')
        
        import time
        start_time = time.time()
        response = requests.get(url, timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f'Response time: {response_time:.3f} seconds')
        
        self.assertEqual(
            response.status_code, 200,
            f"Error en la petición API a {url}"
        )
        
        # Verifica que responde en menos de 10 segundos
        self.assertLess(
            response_time, 10.0,
            f"API response time too slow: {response_time:.3f}s"
        )
        
        print('End - Response Time Test')
        print('---------------------------------------')

    def test_api_get_nonexistent_todo(self):
        """Verifica el comportamiento con un TODO inexistente (solo lectura)"""
        print('---------------------------------------')
        print('Starting - Get Non-existent TODO Test')
        
        # Usa un ID que probablemente no existe
        fake_id = "00000000-0000-0000-0000-000000000000"
        url = BASE_URL + f"/todos/{fake_id}"
        print(f'URL: {url}')
        
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        
        print(f'Response Status: {response.status_code}')
        
        # Debe devolver 404 para un TODO inexistente
        self.assertEqual(
            response.status_code, 404,
            "Debe devolver 404 para TODO inexistente"
        )
        
        print('End - Get Non-existent TODO Test')
        print('---------------------------------------')