from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException 
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import json
import pandas as pd
import csv
from datetime import datetime
from time import sleep
from functools import reduce

class Scraper:
    def __init__(self, config, console) -> None:
        """Constructor de la Clase. inicia las propiedades y el navegador

        Args:
            config (dict): contiene las configuraciones como la politica de reintentos, proxy, etc.
            console (obj): para imprimir por consola
        """
        self.cf = config
        self.console = console
        # Inicializa el navegador
        chrome_options= Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--log-level=3')  # 3: SIN REGISTROS; 
        proxy_ip_port = self.cf['proxy_ip_port'] 
        if self.cf['proxy'] and proxy_ip_port:
            proxy = Proxy()
            proxy.proxy_type = ProxyType.MANUAL
            proxy.http_proxy = proxy_ip_port
            proxy.ssl_proxy = proxy_ip_port
            chrome_options.add_argument(f"--proxy-server={proxy_ip_port}")

        self.driver = webdriver.Chrome(options=chrome_options)

    def get_url(self, url):
        """Ingresa la url en el navegador

        Args:
            url (str): url de la consulta: pagina+categoria+sucursal
        """
        max_attempts = self.cf['max_attempts']
        delay_attempts = self.cf['delay_attempts']
        intentos = 0

        while intentos < max_attempts:
            try:
                self.driver.get(url)
                break
            except WebDriverException  as e:
                self.console.error(f"(proxy) Al intentar obtener la url: {url} - Detalle: {e.msg}")
            except Exception as e:
                self.console.error(f"Al intentar obtener la url: {url} - Detalle: {e}")
                
            self.console.info("Reintentando..")
            intentos += 1
            sleep(delay_attempts)

    def get_gallery(self):
        """ Busca los elementos del grid y el json con la informacion de los productos para la categoria actual

        Returns:
            grid_productos: contiene la lista con cada producto de la pagina html
            item_list_element: contiene la lista de los productos en formato json
        """
        max_attempts = self.cf['max_attempts']
        delay_attempts = self.cf['delay_attempts']
        intentos = 0
        grid_productos, item_list_element = None, None

        while intentos < max_attempts:
            # json con los productos
            script_elements= self.find_elements(self.driver, By.XPATH, '//script[@type="application/ld+json"]') # existe para todas las categorias
            item_list_element = None
            for script_element in script_elements:
                dict_script_element = json.loads(script_element.get_attribute('innerHTML'))
                if dict_script_element['@type'] == "ItemList":
                    item_list_element= dict_script_element['itemListElement']
                    break

            # Esperamos para obtener el grid con los productos
            grid_productos= self.wait_element(By.ID, 'gallery-layout-container')
            
            if not item_list_element or not grid_productos:
                intentos += 1
                self.console.info(f'-No se encontraron los elementos de la pagina. Reintentando: quedan {max_attempts-intentos} intentos')
                sleep(delay_attempts)
            else:
                return grid_productos, item_list_element
        
        return grid_productos, item_list_element

    def process_products(self, grid_productos, item_list_element, category):
        """Obtiene la información de los productos y los acumula en una lista

        Args:
            grid_productos (selenium obj): lista de productos html
            item_list_element (json): lista de productos
            category (str): Nombre de la categoria actual

        Returns:
            lista: lista de los productos en diccionarios
        """
        try:
            product_list = []
            grid_items_productos= self.find_elements(grid_productos, By.XPATH, './div') # obtenemos cada elemento del grid
            for item_element, grid_item_producto in zip(item_list_element, grid_items_productos): 
                # iterar los elementos del grid y del json al mismo tiempo (el json no tiene el precio de lista o tachado)
                producto= item_element['item']
                dict_prod= {
                'nombre': producto['name'],
                'precio_publicado': producto['offers']['offers'][0]['price'],
                'categoria': category,
                'SKU': producto['sku'],
                'url_producto': producto['@id'],
                'stock': producto['offers']['offers'][0]['availability'],
                'descripcion': str(producto['description']).replace('\n', ' ').replace('\r', '') # quitamos los espacios
                }
                precio_regular= self.find_element(grid_item_producto, By.CLASS_NAME,'vtex-product-price-1-x-listPrice')
                if precio_regular:
                    dict_prod['precio_regular']= str(precio_regular.text).replace('$ ', '').replace('.', '').replace(',','.') # quitamos el '$ ' al precio
                else:
                    dict_prod['precio_regular']= producto['offers']['offers'][0]['price']

                product_list.append(dict_prod)
                
        except Exception as e:
            self.console.error(f'(Procesar producto): {e}')
            self.console.info('\n',grid_productos)
            self.console.info('\n',item_list_element)
        
        return product_list

    def process_category(self, url, category):
        """Para la categoria actual: ingresa la url en el navegador, obtiene la información de todos los 
        productos y devuelve la lista

        Args:
            url (str): url de la categoria a procesar
            category (str): Nombre de la categoria

        Returns:
            lista: lista de los productos
        """
        product_list= []
        while True:
            self.get_url(url)
            grid_productos, item_list_element = self.get_gallery()
            if not grid_productos or not item_list_element:    # si el json no tiene productos y no encuentra el grid, retorna lista vacia.En caso de usar luego
                return []
            
            actual_product_list = self.process_products(grid_productos, item_list_element, category) #lista de productos pagina actual

            if actual_product_list:
                product_list.append(actual_product_list)
                if self.more_pages(): 
                    url = self.next_page(url)
                    continue
            
            return self.flatten(product_list)

    def process_branch(self, branch, categories):
        """ MÉTODO PRINCIPAL    
        Para la sucursal actual, extrae todos los productos para todas las categorias y los almacena en un .csv
        por cada categoria

        Args:
            branch (dict): diccionario con el nombre y el codigo(para construir la url) de la sucursal 
            categories (list): lista completa de las categorias
        """
        CONTROL = 0
        for category in categories:
            url = f"{category['url']}?sc={branch['codigo']}"
            product_list = self.process_category(url, category['nombre'])  
            if not product_list:
                self.console.info(f'Sin productos en la Categoria: {category['nombre']}. Sucursal: {branch['nombre']} --- {url}\n')
            else:
                self.create_csv(product_list, category['nombre'], branch['nombre'])
                self.console.info(f"== Sucursal {branch['nombre']}:\n---- Categoria {category['nombre']}: {len(product_list)} productos\n")
            #
            if CONTROL == 1:
                break
            CONTROL +=1
        
        self.driver.quit()
    
    def create_csv(self, product_list, category_name, branch_name):
        """Crea un archivo csv

        Args:
            product_list (list): lista de productos
            category_name (str): Nombre de la categoria
            branch_name (str): Nombre de la sucursal
        """
        date = (datetime.today()).strftime('%d-%m-%Y')
        df = pd.DataFrame(product_list)
        ouput= f'{date}__{branch_name}__{category_name}.csv'
        df.to_csv(f'{self.cf['output_dir']}/{ouput}',  quoting=csv.QUOTE_MINIMAL)
        self.console.info(f"* Se ha generado el archivo {ouput}")

    def find_element(self, elemento,  by, value):
        """parameters: 
                elemento: puede ser driver o el elemento para buscar dentro de su html
                by: By.CLASS, By.ID
                value: nombre de la clase, nombre del id.
        """
        try:
            return elemento.find_element(by, value) #elemento puede ser driver
        except NoSuchElementException:
            self.console.info(f"(No se encontro el elemento:'{value}')")
            return False
        except Exception as e:
            self.console.error(f'(find element): {e}')
            return False
    
    def find_elements(self, elemento,  by, value):
        """parameters: 
                elemento: puede ser driver o el elemento para buscar dentro de su html
                by: By.CLASS, By.ID
                value: nombre de la clase, nombre del id.
        """
        try:
            return elemento.find_elements(by, value) #elemento puede ser driver
        except NoSuchElementException:
            self.console.info(f"(No se encontro el elemento: ({by})'{value}')")
            return False
        except Exception as e:
            self.console.error(f"(find elements): {e}")
            return False
    
    def wait_element(self, by, value):
        """espera a que exista el elemento html para obtenerlo

        Args:
            by (By selenium): contiene el tipo de elemento que se obtendrá. class_name, id, etc.
            value (str): Nombre o valor del elemento

        Returns:
            elemento o bool: falso, si no lo encuentra. sino el elemento
        """
        try:
            return WebDriverWait(self.driver, self.cf['timeout']).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            self.console.info(f"Se agoto el tiempo para: {value}")
            return False
        except NoSuchElementException:
            self.console.error(f"No existe: {value}")
            return False
        except Exception as e:
            self.console.error(f'(wait element): {e}')
            return False
    
    def more_pages(self):
        """verifica que el botón 'cargar mas' esté visible en la página

        Returns:
            True o False
        """
        button = self.find_element(self.driver, By.CLASS_NAME, "vtex-search-result-3-x-buttonShowMore")
        if button.is_displayed():
            return True
        else:
            return False

    def next_page(self, url):
        """Calcula la siguiente página. añade o suma una unidad al parametro 'page' de la url

        Args:
            url (str): url de la categoria

        Returns:
            str: url actualizada
        """
        base_url, query_params = url.split('?')
        params = query_params.split('&')
        
        # Buscar el parámetro 'page' y aumentarlo en una unidad.
        for i, param in enumerate(params):
            if param.startswith('page='):
                str, page_number_str = param.split('=')
                page_number = int(page_number_str) + 1
                params[i] = f'{str}={page_number}'
                break
        else:
            params.insert(0,f'page=2')
        
        # Reconstruir la url
        paginated_url = f'{base_url}?{"&".join(params)}'
        self.console.info('- Nueva pagina -')
        return paginated_url
    
    def flatten(self, list):
        """Recibe una lista de listas, devuelve una lista llana de un nivel.

        Args:
            list (list): lista de productos

        Returns:
            list: lista de productos corregida
        """
        return reduce(lambda x, y: x + y, list, [])