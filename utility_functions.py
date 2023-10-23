import yaml 

def get_config():
    """
    Obtiene los datos de configuracion del archivo /config.yml
    """
    try:
        with open("config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)
            return config
    except FileNotFoundError as e:
        print(f"El archivo no se encontró. {e.filename}")
        config = {}
        config['proxy'] = False
        config['proxy_ip_port'] = None
        config['output_dir'] = ''
        config['thread_number']= 1
        config['max_attempts']= 0
        config['delay_attempts']= 1
        return config