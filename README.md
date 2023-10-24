# auto_scraping_libertad
![hiper libertad](https://hiperlibertad.vtexassets.com/assets/vtex/assets-builder/hiperlibertad.fizzmod-theme/1.17.1/img/retailStoreLogo___647637fa923edf985acb24aa6915109e.svg)
Scraping test challenge for AUTOscraping. Page: _hiperlibertad.com.ar_
Version of python: **Python 3.12.0**, and Selenium, Request libraries.
The goal is to get all products from the page and save them into csv files, one for every category, for every branch.
 
Output format: date__branch-name__category-name.csv
>f.e: '31-10-2023__SUCURSAL__TV LED Y SMART TV.csv'

### To config the script it was used a yaml file: 'config.yaml'
```yaml
proxy: True     # indicate if proxy will be use to connect.
proxy_ip_port: 35.236.207.242:33333     # proxy port 
output_dir: C:\Users\LNKIZ\Desktop\testScrapingHLibertad\auto_scraping_libertad\salida  # folder dir where files will be saved
thread_number: 2    # number of threads
max_attempts: 2     # number of attempts if a connection could not be established.
delay_attempts: 3   # waiting seconds in every attempt
timeout: 10         # waiting time until elements appear in the page
categories_url: https://www.hiperlibertad.com.ar/api/catalog_system/pub/category/tree/3 # url to categories json file.
```
## Libraries
- [selenium](https://selenium-python.readthedocs.io/index.html#): To access pages and get its information.
- [requests](https://requests.readthedocs.io/): to make http requets.
- [PyYAML](https://pyyaml.org/): To manage the configuration.
- [pandas](https://pandas.pydata.org/docs/index.html): To create the csv files.

## How to use:
- Clone the project
```
git clone https://github.com/CarlosABrizuela/auto_scraping_libertad.git 
```
```
cd auto_scraping_libertad
```
- Install the libraries
```
pip install -r requirements.txt
```
- run the script
```
python main.py
```

## Licencia
- Sin Licencia

