import logging
import os
from configparser import ConfigParser

from cltl.combot.infra.di_container import singleton
from cltl.combot.infra.config.api import Configuration, ConfigurationManager, ConfigurationContainer

logger = logging.getLogger(__name__)


_DELIMITER = ","

CONFIG = "config/default.config"
ADDITIONAL_CONFIGS = ["config/pepper.config", "config/credentials.config"]
SECTION_ENVIRONMENT = "environment"


def load_configuration(config_file=CONFIG, additional_config_files=ADDITIONAL_CONFIGS):
    config = ConfigParser({}, strict=False)
    if config_file:
        with open(config_file, 'r') as cfg:
            config.read_file(cfg)
    if additional_config_files:
        config.read(additional_config_files)

    if config.has_section(SECTION_ENVIRONMENT):
        for key, value in config.items(SECTION_ENVIRONMENT):
            # items(section) includes also all entries from the default section
            if key not in config.defaults():
                # keys are converted to lower case by ConfigParser
                os.environ[key.upper()] = value

    logger.info("Loaded configuration: %s",
                {section: dict(config[section])
                 for section in config.sections() + ["DEFAULT"]})

    return config


class LocalConfigurationContainer(ConfigurationContainer):
    __config = None

    @staticmethod
    def load_configuration(config_file=CONFIG, additional_config_files=ADDITIONAL_CONFIGS):
        LocalConfigurationContainer.__config = load_configuration(config_file, additional_config_files)

    @staticmethod
    def get_config(name, key):
        return LocalConfigurationContainer.__config.get(name, key)

    @property
    @singleton
    def config_manager(self):
        if not LocalConfigurationContainer.__config:
            raise ValueError("No configuration loaded")

        return LocalConfigurationManager(LocalConfigurationContainer.__config)


class LocalConfigurationManager(ConfigurationManager):
    def __init__(self, config):
        self._config = config

    def get_config(self, name, callback=None):
        if callback:
            callback(LocalConfig(self._config, name))

        return LocalConfig(self._config, name)


class LocalConfig(Configuration):
    def __init__(self, parser, section):
        # type: (ConfigParser, str) -> None
        self._parser = parser
        self._section = section

    def get(self, key, multi=False):
        # TODO Python 3 Cast to string (instead of unicode string)
        val = str(self._parser.get(self._section, key))

        return val if not multi else [v.strip() for v in val.split(_DELIMITER)]

    def get_int(self, key):
        return self._parser.getint(self._section, key)

    def get_float(self, key):
        return self._parser.getfloat(self._section, key)

    def get_boolean(self, key):
        return self._parser.getboolean(self._section, key)

    def get_enum(self, key, type, multi=False):
        value = self.get(key, multi)
        string_values = value if multi else [value]
        enum_vals = [getattr(type, val.strip().upper()) for val in string_values]

        return enum_vals if multi else enum_vals[0]

    def __contains__(self, key):
        return self._parser.items(self._section).__contains__(key)

    def __iter__(self):
        return self._parser.items(self._section).__iter__()

    def __len__(self):
        return self._parser.items(self._section).__len__()
