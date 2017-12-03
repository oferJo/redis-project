import ruamel.yaml as yaml
import warnings

warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)

with open("config.yml", 'r') as config_file:
    config_dict = yaml.load(config_file)

print config_dict["server_port"]
