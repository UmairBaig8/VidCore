import yaml
from core.paths import config_path


def load_config():
    with open(config_path()) as f:
        return yaml.safe_load(f)
