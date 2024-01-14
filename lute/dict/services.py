from lute.config.app_config import AppConfig
import yaml

def load_mdxdict_config():
    app_conf_path = AppConfig.default_config_filename()
    dict_path = AppConfig(app_conf_path).dictpath
    d={}
    with open(dict_path,'r') as f:
        d= yaml.safe_load(f)
    return d