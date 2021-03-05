import os
from configparser import ConfigParser

from cltl.combot.infra.di_container import singleton
from .api import Configuration, ConfigurationManager, ConfigurationContainer
from .local import LocalConfigurationContainer

_DELIMITER = ","

K8_CONFIG = "cltl_k8_config"

_CONFIG = "config/default.config"
_ADDITIONAL_CONFIGS = ("config/pepper.config", "config/credentials.config")
_SECTION_ENVIRONMENT = "environment"


class K8ConfigurationContainer(ConfigurationContainer):
    @property
    @singleton
    def config_manager(self):
        return K8ConfigurationManager()


class K8ConfigurationManager(ConfigurationManager):
    def __init__(self, config_file=_CONFIG, additional_config_files=_ADDITIONAL_CONFIGS,
                 k8_config=K8_CONFIG):
        self._config = ConfigParser({}, strict=False)

        k8_configs = tuple(os.listdir(k8_config))
        self._load_local_config(config_file, tuple(additional_config_files) + k8_configs)

    def _load_local_config(self, config_file, additional_config_files):
        with open(config_file) as cfg:
            self._config.read_file(cfg)
        self._config.read(additional_config_files)

        if self._config.has_section(_SECTION_ENVIRONMENT):
            for key, value in self._config.items(_SECTION_ENVIRONMENT):
                # items(section) includes also all entries from the default section
                if key not in self._config.defaults():
                    # keys are converted to lower case by ConfigParser
                    os.environ[key.upper()] = value

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
