
![hiper libertad](https://hiperlibertad.vtexassets.com/assets/vtex/assets-builder/hiperlibertad.fizzmod-theme/1.17.1/img/retailStoreLogo___647637fa923edf985acb24aa6915109e.svg)
# auto_scraping_libertad
Scraping test challenge for AUTOscraping. Page: _hiperlibertad.com.ar_

Version of python: **Python 3.12.0**, and Selenium, Request libraries.
The goal is to get all products from the page and save them into csv files, one for every category, for every branch.

To achieve this, first we get the list of categories from the website, and setting it up with the page and branch parameter, as follow.

- url formation
```
base url        : https://www.hiperlibertad.com.ar
categoria url   : /hogar/bano
page url        : ?page=1
sucursal url    : ?sc=1
```
> 'https://www.hiperlibertad.com.ar/hogar/bano?page=1&sc=9'
 
inside most of those pages, exist a json string, wrapped in a script tag <script type="application/ld+json">. where we get products information from. except of regular price, that we get from the list of products html.
Doing this for every category, for every branch.

- Output format: **date**__**branch-name**__**category-name****.csv**
>'31-10-2023__SUCURSAL__TV LED Y SMART TV.csv'

### To config the script it was used a yaml file: 'config.yaml'
> [!NOTE]
> Change before run.
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

