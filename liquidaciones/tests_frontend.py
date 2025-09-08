from django.test import TestCase, Client
from django.urls import reverse
# Selenium imports - optional for basic testing
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
import time
import json

from clientes.models import Cliente
from liquidaciones.models import Procedencia, Proveedor
from items.models import Item


class AutocompleteFrontendTestCase(TestCase):
    """Test autocomplete functionality in the browser"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Set up Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox") 
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        if SELENIUM_AVAILABLE:
            try:
                cls.driver = webdriver.Chrome(options=chrome_options)
                cls.driver.implicitly_wait(10)
                cls.selenium_available = True
            except Exception as e:
                cls.selenium_available = False
                print(f"Selenium not available: {e}")
        else:
            cls.selenium_available = False
    
    @classmethod 
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        super().tearDownClass()
    
    def setUp(self):
        """Set up test data"""
        if not self.selenium_available:
            self.skipTest("Selenium not available")
            
        # Create test data
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
        
        self.procedencia_py = Procedencia.objects.create(nombre='Paraguay')
        self.proveedor1 = Proveedor.objects.create(
            nombre='Proveedor Paraguay S.A.',
            procedencia=self.procedencia_py
        )
        
        self.item1 = Item.objects.create(descripcion='Producto Test A')
        
    def test_cliente_autocomplete_frontend(self):
        """Test cliente autocomplete in browser"""
        if not self.selenium_available:
            self.skipTest("Selenium not available")
            
        # Navigate to liquidacion create form
        self.driver.get(f"{self.live_server_url}/liquidaciones/crear/")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cliente-autocomplete"))
        )
        
        # Find cliente autocomplete input
        cliente_input = self.driver.find_element(By.CLASS_NAME, "cliente-autocomplete")
        
        # Type in the input
        cliente_input.send_keys("juan")
        
        # Wait for autocomplete results to appear
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "autocomplete-item"))
            )
            
            # Check if results appeared
            results = self.driver.find_elements(By.CLASS_NAME, "autocomplete-item")
            self.assertGreater(len(results), 0)
            
            # Check if the correct result is there
            result_text = results[0].text
            self.assertIn("Juan Pérez", result_text)
            
        except TimeoutException:
            # If autocomplete doesn't appear, capture screenshot for debugging
            self.driver.save_screenshot('/tmp/cliente_autocomplete_test.png')
            self.fail("Cliente autocomplete results did not appear within 5 seconds")
    
    def test_proveedor_autocomplete_frontend(self):
        """Test proveedor autocomplete in browser"""
        if not self.selenium_available:
            self.skipTest("Selenium not available")
            
        # Navigate to liquidacion create form
        self.driver.get(f"{self.live_server_url}/liquidaciones/crear/")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "proveedor-autocomplete"))
        )
        
        # Find proveedor autocomplete input
        proveedor_input = self.driver.find_element(By.CLASS_NAME, "proveedor-autocomplete")
        
        # Type in the input
        proveedor_input.send_keys("paraguay")
        
        # Wait for autocomplete results to appear
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "autocomplete-item"))
            )
            
            # Check if results appeared
            results = self.driver.find_elements(By.CLASS_NAME, "autocomplete-item")
            self.assertGreater(len(results), 0)
            
            # Check if the correct result is there with procedencia
            result_text = results[0].text
            self.assertIn("Paraguay", result_text)
            self.assertIn("(Paraguay)", result_text)
            
        except TimeoutException:
            # If autocomplete doesn't appear, capture screenshot for debugging
            self.driver.save_screenshot('/tmp/proveedor_autocomplete_test.png')
            self.fail("Proveedor autocomplete results did not appear within 5 seconds")


class AccentHandlingTests(TestCase):
    """Test handling of accents and special characters"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data with accents
        self.cliente_accents = Cliente.objects.create(
            nombre='José María Fernández',
            ruc='12345678',
            email='jose@example.com'
        )
        
        self.procedencia_accents = Procedencia.objects.create(nombre='São Paulo')
        self.proveedor_accents = Proveedor.objects.create(
            nombre='Proveedora São Paulo Ltda',
            procedencia=self.procedencia_accents
        )
    
    def test_cliente_autocomplete_with_accents(self):
        """Test cliente search with accented characters"""
        url = reverse('cliente_autocomplete')
        
        # Search with accents
        response = self.client.get(url + '?q=josé')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['text'], 'José María Fernández')
        
        # Search without accents should also work
        response = self.client.get(url + '?q=jose')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        
        # Search with partial accented name
        response = self.client.get(url + '?q=maría')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
    
    def test_proveedor_autocomplete_with_accents(self):
        """Test proveedor search with accented characters"""
        url = reverse('proveedor_autocomplete')
        
        # Search with accents in procedencia
        response = self.client.get(url + '?q=são')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        result = data['results'][0]
        self.assertIn('São Paulo', result['text'])
        
        # Search by proveedor name with accents
        response = self.client.get(url + '?q=proveedora')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)


class AutocompleteEdgeCasesTests(TestCase):
    """Test edge cases and special scenarios"""
    
    def setUp(self):
        self.client = Client()
        
        # Create edge case data
        self.cliente_special = Cliente.objects.create(
            nombre='Cliente & Co. S.A.',
            ruc='12345678',
            email='cliente@example.com'
        )
        
        self.procedencia_special = Procedencia.objects.create(nombre='U.S.A.')
        self.proveedor_special = Proveedor.objects.create(
            nombre='Provider & Co.',
            procedencia=self.procedencia_special
        )
    
    def test_autocomplete_with_special_characters(self):
        """Test autocomplete with special characters like &, ., etc."""
        url = reverse('cliente_autocomplete')
        
        response = self.client.get(url + '?q=&')
        data = json.loads(response.content)
        
        self.assertEqual(len(data['results']), 1)
        self.assertIn('Cliente & Co.', data['results'][0]['text'])
    
    def test_autocomplete_with_very_short_query(self):
        """Test autocomplete behavior with very short queries"""
        url = reverse('cliente_autocomplete')
        
        # Single character - should return empty results
        response = self.client.get(url + '?q=c')
        data = json.loads(response.content)
        self.assertEqual(data['results'], [])
        
        # Two characters - should work
        response = self.client.get(url + '?q=cl')
        data = json.loads(response.content)
        # May or may not have results, but should not error
        self.assertIsInstance(data['results'], list)
    
    def test_autocomplete_case_sensitivity_edge_cases(self):
        """Test various case combinations"""
        url = reverse('cliente_autocomplete')
        
        test_queries = ['CLIENTE', 'cliente', 'Cliente', 'cLiEnTe']
        
        for query in test_queries:
            with self.subTest(query=query):
                response = self.client.get(url + f'?q={query}')
                data = json.loads(response.content)
                
                # All should return the same result
                if len(data['results']) > 0:
                    self.assertIn('Cliente & Co.', data['results'][0]['text'])


# Simple function to run basic tests without Selenium
def run_basic_frontend_tests():
    """
    Function to run basic frontend tests without requiring Selenium
    This can be called from manage.py shell for quick testing
    """
    import requests
    import time
    from django.test.utils import setup_test_environment, teardown_test_environment
    from django.test.runner import DiscoverRunner
    
    print("Running basic frontend autocomplete tests...")
    
    # Test URLs
    base_url = "http://localhost:8000"
    
    test_urls = [
        f"{base_url}/liquidaciones/api/cliente-autocomplete/?q=test",
        f"{base_url}/liquidaciones/api/proveedor-autocomplete/?q=test", 
        f"{base_url}/liquidaciones/api/item-autocomplete/?q=test"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {url} - OK (returned {len(data.get('results', []))} results)")
            else:
                print(f"✗ {url} - ERROR: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ {url} - ERROR: {e}")
    
    print("Basic frontend tests completed.")


if __name__ == '__main__':
    run_basic_frontend_tests()