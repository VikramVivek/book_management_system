import logging
import logging.config
import os

import yaml


def setup_logging(
    default_path="logging.yaml", default_level=logging.INFO, env_key="LOG_CFG"
):
    """
    Setup logging configuration.

    This function sets up logging based on a configuration file in YAML format.
    If the file is not found, it falls back to a basic logging configuration.

    Args:
        default_path (str): The default path to the logging configuration file.
        default_level (int): The default logging level if the config file is not found.
        env_key (str): The environment variable that can override the path to the
                       logging configuration file.
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        logging.info(f"Logging configured using {path}")
    else:
        logging.basicConfig(level=default_level)
        logging.warning(
            f"Logging configuration file not found: {path}. Using default config"
        )


# Initialize logging configuration when the module is imported
setup_logging()
