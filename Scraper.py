from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import json
import pandas as pd
import csv
from datetime import datetime
import logging
from time import sleep

class Scraper:
    def __init__(self, config) -> None:
        self.cf = config
        # Inicializa el navegador
        chrome_options= Options()
        # chrome_options.add_argument('--headless')
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
        #
        # Configuración del logger
        self.console = logging.getLogger("console_logger")
        self.console.setLevel(logging.DEBUG)  
        console_handler = logging.StreamHandler() 
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        self.console.addHandler(console_handler)

    def create_csv(self, product_list, category_name, name_branch):
        date = (datetime.today()).strftime('%d-%m-%Y')
        df = pd.DataFrame(product_list)
        ouput= f'{date}__{name_branch}__{category_name}.csv'
        df.to_csv(f'{self.cf['output_dir']}/{ouput}',  quoting=csv.QUOTE_MINIMAL)
        self.console.info(f"* Se ha generado el archivo {ouput}")

    def process_product(self, grid_productos, item_list_element):
        try:
            product_list = []
            grid_items_productos= self.find_elements(grid_productos, By.XPATH, './div') # obtenemos cada elemento del grid
            for item_element, grid_item_producto in zip(item_list_element, grid_items_productos): 
                # iterar los elementos del grid y del json al mismo tiempo (el json no tiene el precio de lista o tachado)
                producto= item_element['item']
                dict_prod= {
                'nombre': producto['name'],
                'precio_publicado': producto['offers']['offers'][0]['price'],
                'categoria': "CATEGORIA",
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
            print('\n',grid_productos)
            print('\n',item_list_element)
        
        return product_list

    def process_category(self, url):
        self.driver.get(url)
        sleep(3)
        item_list_element= None
        script_elements= self.find_elements(self.driver, By.XPATH, '//script[@type="application/ld+json"]')
        print(f"scripts: ", len(script_elements))
        for script_element in script_elements:
            dict_script_element = json.loads(script_element.get_attribute('innerHTML'))
            print(f"type: ", dict_script_element['@type'])
            if dict_script_element['@type'] == "ItemList":
                item_list_element= dict_script_element['itemListElement']

        grid_productos= self.wait_element(By.ID, 'gallery-layout-container')

        return self.process_product(grid_productos, item_list_element)
        

    def run(self, categories):
        control = 0
        for category in categories:
            self.console.info(f"Procesando: {category['nombre']}")
            url = f"{category['url']}?sc=2"
            print(url)
            product_list = self.process_category(url) # hardcode de la sucursal 
            self.create_csv(product_list, category['nombre'], "SUCURSAL")
            #
            if control == 1:
                break
            control +=1
    
    def find_element(self, elemento,  by, value):
        """parameters: 
                elemento: puede ser driver o el elemento para buscar dentro de su html
                by: By.CLASS, By.ID
                value: nombre de la clase, nombre del id.
        """
        try:
            return elemento.find_element(by, value) #elemento puede ser driver
        except NoSuchElementException:
            print(f"No se encontro el elemento:'{value}'")
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
            print(f"No se encontro el elemento: ({by})'{value}'")
            return False
        except Exception as e:
            self.console.error(f"(find elements): {e}")
            return False
    
    def wait_element(self, by, value):
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
