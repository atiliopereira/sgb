from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import json

from clientes.models import Cliente
from liquidaciones.models import Procedencia, Proveedor, Liquidacion
from items.models import Item


class AutocompleteTestCase(TestCase):
    """Tests for autocomplete functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test clientes
        self.cliente1 = Cliente.objects.create(
            nombre='Juan Pérez',
            ruc='12345678',
            email='juan@example.com'
        )
        self.cliente2 = Cliente.objects.create(
            nombre='María García López',
            ruc='87654321',
            email='maria@example.com'
        )
        self.cliente3 = Cliente.objects.create(
            nombre='Pedro Martínez',
            ruc='11223344',
            email='pedro@example.com'
        )
        
        # Create test procedencias
        self.procedencia_py = Procedencia.objects.create(nombre='Paraguay')
        self.procedencia_br = Procedencia.objects.create(nombre='Brasil')
        self.procedencia_ar = Procedencia.objects.create(nombre='Argentina')
        
        # Create test proveedores
        self.proveedor1 = Proveedor.objects.create(
            nombre='Proveedor Paraguay S.A.',
            procedencia=self.procedencia_py
        )
        self.proveedor2 = Proveedor.objects.create(
            nombre='Importadora Brasil Ltda',
            procedencia=self.procedencia_br
        )
        self.proveedor3 = Proveedor.objects.create(
            nombre='Exportadora Argentina SRL',
            procedencia=self.procedencia_ar
        )
        self.proveedor4 = Proveedor.objects.create(
            nombre='Comercial Paraguay',
            procedencia=self.procedencia_py
        )
        
        # Create test items
        self.item1 = Item.objects.create(descripcion='Producto A')
        self.item2 = Item.objects.create(descripcion='Producto B Special')
        self.item3 = Item.objects.create(descripcion='Item C')


class ClienteAutocompleteTests(AutocompleteTestCase):
    """Tests for cliente autocomplete API"""
    
    def test_cliente_autocomplete_url_exists(self):
        """Test that the cliente autocomplete URL exists"""
        url = reverse('cliente_autocomplete')
        response = self.client.get(url + '?q=juan')
        self.assertEqual(response.status_code, 200)
    
    def test_cliente_autocomplete_returns_json(self):
        """Test that cliente autocomplete returns valid JSON"""
        url = reverse('cliente_autocomplete')
        response = self.client.get(url + '?q=juan')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Should be valid JSON
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
    
    def test_cliente_autocomplete_search_by_name(self):
        """Test cliente autocomplete search by name"""
        url = reverse('cliente_autocomplete')
        
        # Search for 'juan'
        response = self.client.get(url + '?q=juan')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['text'], 'Juan Pérez')
        self.assertEqual(data['results'][0]['id'], self.cliente1.id)
    
    def test_cliente_autocomplete_case_insensitive(self):
        """Test that cliente autocomplete is case insensitive"""
        url = reverse('cliente_autocomplete')
        
        # Search for 'JUAN' (uppercase)
        response = self.client.get(url + '?q=JUAN')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['text'], 'Juan Pérez')
    
    def test_cliente_autocomplete_partial_match(self):
        """Test partial name matching"""
        url = reverse('cliente_autocomplete')
        
        # Search for 'garcía' (should find María García López)
        response = self.client.get(url + '?q=garcía')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['text'], 'María García López')
    
    def test_cliente_autocomplete_multiple_results(self):
        """Test that autocomplete returns multiple matching results"""
        url = reverse('cliente_autocomplete')
        
        # Search for 'ar' (should find María García and Pedro Martínez)
        response = self.client.get(url + '?q=ar')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 2)
        result_names = [result['text'] for result in data['results']]
        self.assertIn('María García López', result_names)
        self.assertIn('Pedro Martínez', result_names)
    
    def test_cliente_autocomplete_empty_query(self):
        """Test autocomplete with empty query"""
        url = reverse('cliente_autocomplete')
        
        response = self.client.get(url + '?q=')
        data = json.loads(response.content)
        
        self.assertEqual(data['results'], [])
    
    def test_cliente_autocomplete_no_matches(self):
        """Test autocomplete with query that has no matches"""
        url = reverse('cliente_autocomplete')
        
        response = self.client.get(url + '?q=nonexistent')
        data = json.loads(response.content)
        
        self.assertEqual(data['results'], [])
    
    def test_cliente_autocomplete_limit_results(self):
        """Test that autocomplete limits results to 10"""
        # Create 15 clientes with similar names
        for i in range(15):
            Cliente.objects.create(
                nombre=f'Test Cliente {i:02d}',
                ruc=f'1000000{i:02d}',
                email=f'test{i:02d}@example.com'
            )
        
        url = reverse('cliente_autocomplete')
        response = self.client.get(url + '?q=test')
        data = json.loads(response.content)
        
        # Should limit to 10 results
        self.assertEqual(len(data['results']), 10)


class ProveedorAutocompleteTests(AutocompleteTestCase):
    """Tests for proveedor autocomplete API"""
    
    def test_proveedor_autocomplete_url_exists(self):
        """Test that the proveedor autocomplete URL exists"""
        url = reverse('proveedor_autocomplete')
        response = self.client.get(url + '?q=paraguay')
        self.assertEqual(response.status_code, 200)
    
    def test_proveedor_autocomplete_returns_json(self):
        """Test that proveedor autocomplete returns valid JSON"""
        url = reverse('proveedor_autocomplete')
        response = self.client.get(url + '?q=paraguay')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Should be valid JSON
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
    
    def test_proveedor_autocomplete_search_by_name(self):
        """Test proveedor autocomplete search by proveedor name"""
        url = reverse('proveedor_autocomplete')
        
        response = self.client.get(url + '?q=importadora')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['text'], 'Importadora Brasil Ltda (Brasil)')
        self.assertEqual(data['results'][0]['id'], self.proveedor2.id)
    
    def test_proveedor_autocomplete_search_by_procedencia(self):
        """Test proveedor autocomplete search by procedencia name"""
        url = reverse('proveedor_autocomplete')
        
        response = self.client.get(url + '?q=paraguay')
        data = json.loads(response.content)
        
        # Should find both proveedores from Paraguay
        self.assertEqual(len(data['results']), 2)
        result_texts = [result['text'] for result in data['results']]
        self.assertIn('Proveedor Paraguay S.A. (Paraguay)', result_texts)
        self.assertIn('Comercial Paraguay (Paraguay)', result_texts)
    
    def test_proveedor_autocomplete_format(self):
        """Test that proveedor results include procedencia in format"""
        url = reverse('proveedor_autocomplete')
        
        response = self.client.get(url + '?q=exportadora')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        result = data['results'][0]
        
        # Should include procedencia in parentheses
        self.assertEqual(result['text'], 'Exportadora Argentina SRL (Argentina)')
        self.assertIn('(Argentina)', result['text'])
    
    def test_proveedor_autocomplete_case_insensitive(self):
        """Test that proveedor autocomplete is case insensitive"""
        url = reverse('proveedor_autocomplete')
        
        response = self.client.get(url + '?q=BRASIL')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['text'], 'Importadora Brasil Ltda (Brasil)')
    
    def test_proveedor_autocomplete_empty_query(self):
        """Test proveedor autocomplete with empty query"""
        url = reverse('proveedor_autocomplete')
        
        response = self.client.get(url + '?q=')
        data = json.loads(response.content)
        
        self.assertEqual(data['results'], [])
    
    def test_proveedor_autocomplete_no_matches(self):
        """Test proveedor autocomplete with query that has no matches"""
        url = reverse('proveedor_autocomplete')
        
        response = self.client.get(url + '?q=nonexistent')
        data = json.loads(response.content)
        
        self.assertEqual(data['results'], [])
    
    def test_proveedor_autocomplete_with_null_procedencia(self):
        """Test proveedor autocomplete with proveedores that have null procedencia"""
        # Create proveedor with null procedencia
        proveedor_null = Proveedor.objects.create(
            nombre='Proveedor Sin Procedencia',
            procedencia=None
        )
        
        url = reverse('proveedor_autocomplete')
        response = self.client.get(url + '?q=sin')
        data = json.loads(response.content)
        
        # Should handle null procedencia gracefully
        self.assertEqual(response.status_code, 200)


class ItemAutocompleteTests(AutocompleteTestCase):
    """Tests for item autocomplete API"""
    
    def test_item_autocomplete_url_exists(self):
        """Test that the item autocomplete URL exists"""
        url = reverse('item_autocomplete')
        response = self.client.get(url + '?q=producto')
        self.assertEqual(response.status_code, 200)
    
    def test_item_autocomplete_returns_json(self):
        """Test that item autocomplete returns valid JSON"""
        url = reverse('item_autocomplete')
        response = self.client.get(url + '?q=producto')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
    
    def test_item_autocomplete_search(self):
        """Test item autocomplete search functionality"""
        url = reverse('item_autocomplete')
        
        response = self.client.get(url + '?q=producto')
        data = json.loads(response.content)
        
        # Should find 2 products with 'producto' in name
        self.assertEqual(len(data['results']), 2)
        result_texts = [result['text'] for result in data['results']]
        self.assertIn('Producto A', result_texts)
        self.assertIn('Producto B Special', result_texts)
    
    def test_item_autocomplete_case_insensitive(self):
        """Test that item autocomplete is case insensitive"""
        url = reverse('item_autocomplete')
        
        response = self.client.get(url + '?q=PRODUCTO')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 2)
    
    def test_item_autocomplete_partial_match(self):
        """Test item partial matching"""
        url = reverse('item_autocomplete')
        
        response = self.client.get(url + '?q=special')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['text'], 'Producto B Special')


class IntegrationTests(AutocompleteTestCase):
    """Integration tests for autocomplete functionality"""
    
    def test_liquidacion_form_loads_with_autocomplete(self):
        """Test that liquidacion form loads and includes autocomplete JavaScript"""
        url = reverse('liquidacion_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cliente-autocomplete')
        self.assertContains(response, 'proveedor-autocomplete')
        self.assertContains(response, 'initializeClienteAutocomplete')
        self.assertContains(response, 'initializeProveedorAutocomplete')
    
    def test_autocomplete_api_endpoints_in_javascript(self):
        """Test that JavaScript calls the correct API endpoints"""
        url = reverse('liquidacion_create')
        response = self.client.get(url)
        
        # Check that the JavaScript includes the correct API endpoints
        self.assertContains(response, '/liquidaciones/api/cliente-autocomplete/')
        self.assertContains(response, '/liquidaciones/api/proveedor-autocomplete/')
        self.assertContains(response, '/liquidaciones/api/item-autocomplete/')
    
    def test_autocomplete_performance(self):
        """Test autocomplete performance with larger dataset"""
        import time
        
        # Create larger dataset
        for i in range(100):
            Cliente.objects.create(
                nombre=f'Performance Test Cliente {i:03d}',
                ruc=f'2000000{i:03d}',
                email=f'perf{i:03d}@example.com'
            )
        
        url = reverse('cliente_autocomplete')
        
        start_time = time.time()
        response = self.client.get(url + '?q=performance')
        end_time = time.time()
        
        # Should respond in less than 1 second
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0)
        
        # Should still limit to 10 results
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 10)


class ErrorHandlingTests(TestCase):
    """Tests for error handling in autocomplete"""
    
    def setUp(self):
        self.client = Client()
    
    def test_autocomplete_missing_query_param(self):
        """Test autocomplete without q parameter"""
        urls = [
            reverse('cliente_autocomplete'),
            reverse('proveedor_autocomplete'),
            reverse('item_autocomplete')
        ]
        
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                
                data = json.loads(response.content)
                self.assertEqual(data['results'], [])
    
    def test_autocomplete_invalid_query_param(self):
        """Test autocomplete with very long query"""
        very_long_query = 'a' * 1000
        urls = [
            reverse('cliente_autocomplete'),
            reverse('proveedor_autocomplete'), 
            reverse('item_autocomplete')
        ]
        
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url + f'?q={very_long_query}')
                # Should not crash
                self.assertEqual(response.status_code, 200)
                
                data = json.loads(response.content)
                self.assertIsInstance(data['results'], list)